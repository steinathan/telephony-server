from typing import Optional
import typing

import sentry_sdk
from fastapi import APIRouter, HTTPException, WebSocket
from loguru import logger

from streaming_providers.base import BaseStreamingProvider
from streaming_providers.default_factory import (
    AbstractStreamingProviderFactory,
    DefaultStreamingProviderFactory,
)
from streaming_providers.models import StreamingProviderConfig
from telephony.config_manager.base_config_manager import (
    BaseCallConfig,
    BaseConfigManager,
)
from telephony.models.telephony import TwilioCallConfig
from telephony.server.conversation.abstract_phone_conversation import (
    AbstractPhoneConversation,
)
from telephony.server.conversation.twilio_phone_conversation import (
    TwilioPhoneConversation,
)
from telephony.server.output_devices.abstract_output_device import AbstractOutputDevice
from telephony.utils.events_manager import EventsManager


class CallsRouter:
    def __init__(
        self,
        base_url: str,
        config_manager: BaseConfigManager,
        streaming_factory: AbstractStreamingProviderFactory,
        # streaming_provider_config: StreamingProviderConfig,
        events_manager: EventsManager | None = None,
    ):
        super().__init__()
        self.base_url = base_url
        self.streaming_factory = streaming_factory
        self.config_manager = config_manager
        self.events_manager = events_manager
        # self.streaming_provider_config = streaming_provider_config

        self.router = APIRouter()
        self.router.websocket("/connect_call/{id}")(self.connect_call)

    def _from_call_config(
        self,
        streaming_provider: BaseStreamingProvider,
        base_url: str,
        call_config: BaseCallConfig,
        config_manager: BaseConfigManager,
        conversation_id: str,
        device: AbstractOutputDevice,
        events_manager: Optional[EventsManager] = None,
    ) -> AbstractPhoneConversation:
        if isinstance(call_config, TwilioCallConfig):
            return TwilioPhoneConversation(
                streaming_provider=streaming_provider,
                to_phone=call_config.to_phone,
                from_phone=call_config.from_phone,
                base_url=base_url,
                config_manager=config_manager,
                twilio_config=call_config.twilio_config,
                twilio_sid=call_config.twilio_sid,
                conversation_id=conversation_id,
                events_manager=events_manager,
                direction=call_config.direction,
                device=device,
            )
        else:
            raise ValueError(f"Unknown call config type {call_config.type}")

    async def connect_call(self, websocket: WebSocket, id: str):
        with sentry_sdk.start_transaction(op="connect_call") as sentry_txn:
            # sentry_transaction.set(sentry_txn)
            await websocket.accept()

            logger.debug("Phone WS connection opened for chat {}".format(id))
            call_config = await self.config_manager.get_config(id)
            if not call_config:
                raise HTTPException(status_code=400, detail="No active phone call")

            device = AbstractOutputDevice()
            streaming_provider = self.streaming_factory.create_streaming_provider(
                websocket=websocket,
                device=device,  # type: ignore
                streaming_provider_config=call_config.streaming_provider_config,
                call_config=call_config,
                config_manager=self.config_manager,
                events_manager=self.events_manager,
            )

            phone_conversation = self._from_call_config(
                streaming_provider=streaming_provider,
                base_url=self.base_url,
                call_config=call_config,
                config_manager=self.config_manager,
                conversation_id=id,
                events_manager=self.events_manager,
                device=device,
            )

            await phone_conversation.attach_ws_and_start(websocket)
            logger.debug("Phone WS connection closed for chat {}".format(id))

    def get_router(self) -> APIRouter:
        return self.router
