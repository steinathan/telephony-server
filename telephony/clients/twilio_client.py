import os
from typing import Dict, Optional

import aiohttp
from loguru import logger

from telephony.clients.abstract import AbstractTelephonyClient
from telephony.models.telephony import TwilioConfig
from fastapi import Response

from telephony.utils.async_requestor import AsyncRequestor


class TwilioBadRequestException(ValueError):
    pass


class TwilioException(ValueError):
    pass


class TwilioClient(AbstractTelephonyClient):
    def __init__(
        self,
        base_url: str,
        maybe_twilio_config: Optional[TwilioConfig] = None,
    ):
        self.twilio_config = maybe_twilio_config or TwilioConfig(
            account_sid=os.environ["TWILIO_ACCOUNT_SID"],
            auth_token=os.environ["TWILIO_AUTH_TOKEN"],
        )
        self.auth = aiohttp.BasicAuth(
            login=self.twilio_config.account_sid,
            password=self.twilio_config.auth_token,
        )
        super().__init__(base_url=base_url)

    def get_telephony_config(self):
        return self.twilio_config

    async def create_call(
        self,
        conversation_id: str,
        to_phone: str,
        from_phone: str,
        record: bool = False,  # currently no-op
        digits: Optional[str] = None,  # currently no-op
        telephony_params: Optional[Dict[str, str]] = None,
    ) -> str:
        twiml = self.get_connection_twiml(conversation_id=conversation_id).body.decode( # type: ignore
            "utf-8"
        )
        data = {
            "Twiml": twiml,
            "To": f"+{to_phone}",
            "From": f"+{from_phone}",
            **(telephony_params or {}),
        }
        if digits:
            data["SendDigits"] = digits
        async with (
            AsyncRequestor()
            .get_session()
            .post(
                f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_config.account_sid}/Calls.json",
                auth=self.auth,
                data=data,
            ) as response
        ):
            if not response.ok:
                if response.status == 400:
                    logger.warning(
                        f"Failed to create call: {response.status} {response.reason} {await response.json()}"
                    )
                    raise TwilioBadRequestException(
                        "Telephony provider rejected call; this is usually due to a bad/malformed number. "
                    )
                else:
                    raise TwilioException(
                        f"Twilio failed to create call: {response.status} {response.reason}"
                    )
            response = await response.json()
            return response["sid"]

    def get_connection_twiml(self, conversation_id: str):
        twml = f"""
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Connect>
    <Stream url="wss://{self.base_url}/connect_call/{conversation_id}" />
  </Connect>
</Response>
"""
        return Response(
            twml,
            media_type="application/xml",
        )

    async def end_call(self, telephony_id: str) -> bool:
        async with (
            AsyncRequestor()
            .get_session()
            .post(
                f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_config.account_sid}/Calls/{telephony_id}.json",
                auth=self.auth,
                data={"Status": "completed"},
            ) as response
        ):
            if not response.ok:
                raise RuntimeError(
                    f"Failed to end call: {response.status} {response.reason}"
                )
            response = await response.json()
            return response["status"] == "completed"
