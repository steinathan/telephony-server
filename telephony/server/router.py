from typing import Optional

import sentry_sdk
from fastapi import APIRouter, HTTPException, WebSocket
from loguru import logger

from telephony.config_manager.base_config_manager import BaseCallConfig, BaseConfigManager
from telephony.models.telephony import TwilioCallConfig
from telephony.server.conversation.abstract_phone_conversation import AbstractPhoneConversation
from telephony.server.conversation.twilio_phone_conversation import TwilioPhoneConversation
from telephony.utils.events_manager import EventsManager



class CallsRouter:
    def __init__(
        self,
        base_url: str,
        config_manager: BaseConfigManager,
        events_manager: Optional[EventsManager] = None,
    ):
        super().__init__()
        self.base_url = base_url
        self.config_manager = config_manager
        self.events_manager = events_manager
        self.router = APIRouter()
        self.router.websocket("/connect_call/{id}")(self.connect_call)

    def _from_call_config(
        self,
        base_url: str,
        call_config: BaseCallConfig,
        config_manager: BaseConfigManager,
        conversation_id: str,
        events_manager: Optional[EventsManager] = None,
    ) -> AbstractPhoneConversation:
        if isinstance(call_config, TwilioCallConfig):
            return TwilioPhoneConversation(
                to_phone=call_config.to_phone,
                from_phone=call_config.from_phone,
                base_url=base_url,
                config_manager=config_manager,
                twilio_config=call_config.twilio_config,
                twilio_sid=call_config.twilio_sid,
                conversation_id=conversation_id,
                events_manager=events_manager,
                direction=call_config.direction,
            )
        # elif isinstance(call_config, VonageCallConfig):
        #     return VonagePhoneConversation(
        #         to_phone=call_config.to_phone,
        #         from_phone=call_config.from_phone,
        #         base_url=base_url,
        #         config_manager=config_manager,
        #         agent_config=call_config.agent_config,
        #         transcriber_config=call_config.transcriber_config,
        #         synthesizer_config=call_config.synthesizer_config,
        #         vonage_config=call_config.vonage_config,
        #         vonage_uuid=call_config.vonage_uuid,
        #         conversation_id=conversation_id,
        #         transcriber_factory=transcriber_factory,
        #         agent_factory=agent_factory,
        #         synthesizer_factory=synthesizer_factory,
        #         events_manager=events_manager,
        #         output_to_speaker=call_config.output_to_speaker,
        #         direction=call_config.direction,
        #     )
        # elif isinstance(call_config, PlivoCallConfig):
        #     return PlivoPhoneConversation(
        #         plivo_auth_id="",
        #         plivo_auth_token="",
        #         to_phone=call_config.to_phone,
        #         from_phone=call_config.from_phone,
        #         base_url=base_url,
        #         config_manager=config_manager,
        #         agent_config=call_config.agent_config,
        #         transcriber_config=call_config.transcriber_config,
        #         synthesizer_config=call_config.synthesizer_config,
        #         plivo_config=call_config.plivo_config,
        #         # plivo_uuid=call_config.plivo_uuid,
        #         conversation_id=conversation_id,
        #         transcriber_factory=transcriber_factory,
        #         agent_factory=agent_factory,
        #         synthesizer_factory=synthesizer_factory,
        #         events_manager=events_manager,
        #         direction=call_config.direction,
        #     )
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

            phone_conversation = self._from_call_config(
                base_url=self.base_url,
                call_config=call_config,
                config_manager=self.config_manager,
                conversation_id=id,
                events_manager=self.events_manager,
            )

            await phone_conversation.attach_ws_and_start(websocket)
            logger.debug("Phone WS connection closed for chat {}".format(id))

    def get_router(self) -> APIRouter:
        return self.router
