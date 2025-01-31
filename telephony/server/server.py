import abc
from functools import partial
from typing import List, Optional
import typing

from fastapi import APIRouter, Form, Request, Response
from loguru import logger
from pydantic.v1 import BaseModel, Field

from streaming_providers.models import StreamingProviderConfig
from telephony.clients.abstract import AbstractTelephonyClient
from telephony.clients.twilio_client import TwilioClient
from telephony.config_manager.base_config_manager import BaseCallConfig, BaseConfigManager
from telephony.models.events import RecordingEvent
from telephony.models.telephony import TwilioCallConfig, TwilioConfig
from telephony.server.router import CallsRouter
from telephony.utils.events_manager import EventsManager
from telephony.utils.strings import create_conversation_id


class AbstractInboundCallConfig(BaseModel, abc.ABC):
    url: str
    


class TwilioInboundCallConfig(AbstractInboundCallConfig):
    twilio_config: TwilioConfig


class TelephonyServer:
    def __init__(
        self,
        base_url: str,
        config_manager: BaseConfigManager,
        streaming_provider_config: StreamingProviderConfig,
        inbound_call_configs: List[AbstractInboundCallConfig] = [],
        events_manager: Optional[EventsManager] = None,
    ):
        self.base_url = base_url
        self.router = APIRouter()
        self.steaming_provider_config = streaming_provider_config
        self.config_manager = config_manager
        self.events_manager = events_manager
        self.router.include_router(
            CallsRouter(
                base_url=base_url,
                config_manager=self.config_manager,
                events_manager=self.events_manager,
            ).get_router()
        )
        for config in inbound_call_configs:
            self.router.add_api_route(
                config.url,
                self.create_inbound_route(inbound_call_config=config),
                methods=["POST"],
            )
        self.router.add_api_route("/events", self.events, methods=["GET", "POST"])
        logger.info(f"Set up events endpoint at https://{self.base_url}/events")

        self.router.add_api_route(
            "/plivo/get_answer_url/{conversation_id}",
            self.get_pilvo_answer_url,
            methods=["GET", "POST"],
        )
        self.router.add_api_route(
            "/recordings/{conversation_id}", self.recordings, methods=["GET", "POST"]
        )
        logger.info(
            f"Set up recordings endpoint at https://{self.base_url}/recordings/{{conversation_id}}"
        )

    def events(self, request: Request):
        return Response()

    async def get_pilvo_answer_url(self, conversation_id):
        "TODO: Implement Plivo answer URL"
        # xml_response = ""
        # return Response(content=xml_response, media_type="application/xml")
        raise NotImplementedError("Plivo is not yet supported")

    async def recordings(self, request: Request, conversation_id: str):
        recording_url = (await request.json())["recording_url"]
        if self.events_manager is not None and recording_url is not None:
            self.events_manager.publish_event(
                RecordingEvent(
                    recording_url=recording_url, conversation_id=conversation_id
                )
            )
        return Response()

    def create_inbound_route(
        self,
        inbound_call_config: AbstractInboundCallConfig,
    ):
        async def twilio_route(
            twilio_config: TwilioConfig,
            twilio_sid: str = Form(alias="CallSid"),
            twilio_from: str = Form(alias="From"),
            twilio_to: str = Form(alias="To"),
        ) -> Response:
            call_config = TwilioCallConfig(
                twilio_config=twilio_config,
                twilio_sid=twilio_sid,
                from_phone=twilio_from,
                to_phone=twilio_to,
                direction="inbound",
            )
            conversation_id = create_conversation_id("inbound")
            await self.config_manager.save_config(
                conversation_id, typing.cast(BaseCallConfig, call_config)
            )
            twilio_client = TwilioClient(
                base_url=self.base_url, maybe_twilio_config=twilio_config
            )
            return twilio_client.get_connection_twiml(conversation_id)

        if isinstance(inbound_call_config, TwilioInboundCallConfig):
            logger.info(
                f"Set up inbound call TwiML at https://{self.base_url}{inbound_call_config.url}"
            )
            return partial(twilio_route, inbound_call_config.twilio_config)
        else:
            raise ValueError(
                f"Unknown inbound call config type {type(inbound_call_config)}"
            )

    async def end_outbound_call(self, conversation_id: str):
        call_config = await self.config_manager.get_config(conversation_id)
        if not call_config:
            raise ValueError(f"Could not find call config for {conversation_id}")
        telephony_client: AbstractTelephonyClient
        if isinstance(call_config, TwilioCallConfig):
            telephony_client = TwilioClient(
                base_url=self.base_url, maybe_twilio_config=call_config.twilio_config
            )
            await telephony_client.end_call(call_config.twilio_sid)
            return {"id": conversation_id}

    def get_router(self) -> APIRouter:
        return self.router
