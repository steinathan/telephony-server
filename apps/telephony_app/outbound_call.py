import os

from dotenv import load_dotenv

from telephony.config_manager.redis_config_manager import RedisConfigManager
from telephony.models.telephony import TwilioConfig
from telephony.outbound_call import OutboundCall


load_dotenv()


BASE_URL = os.environ["BASE_URL"]


async def main():
    config_manager = RedisConfigManager()

    outbound_call = OutboundCall(
        conversation_id="test_conversation_id",
        base_url=BASE_URL,
        to_phone="+15555555555",
        from_phone="+15555555555",
        config_manager=config_manager,
        telephony_config=TwilioConfig(
            account_sid=os.environ["TWILIO_ACCOUNT_SID"],
            auth_token=os.environ["TWILIO_AUTH_TOKEN"],
        ),
    )

    input("Press enter to start call...")
    await outbound_call.start()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())