import os
from dotenv import load_dotenv


from streaming_providers.models import BaseMessage
from streaming_providers.pipecat.pipecat import PipecatStreamingConfig
from telephony.config_manager.redis_config_manager import RedisConfigManager
from telephony.models.telephony import TwilioConfig
from telephony.outbound_call import OutboundCall

from cuid2 import Cuid

from telephony.utils.strings import create_conversation_id

load_dotenv()


BASE_URL = os.environ["BASE_URL"]


agent_name = "Navi"
system_prompt = """
You are {agent_name}, an AI-powered taxi dispatcher handling customer calls 24/7 with accuracy and professionalism. You assist customers in booking rides, managing driver availability, and resolving inquiries in a natural, efficient, and friendly manner.

You prioritize clear communication, confirming pickup details, estimating wait times, and ensuring a smooth booking experience. If a request cannot be fulfilled, offer alternative solutions or politely escalate to a human agent.

Maintain a warm, professional, and helpful tone. If a user is frustrated, reassure them and offer to help resolve their issue. Always confirm key details and minimize friction in the booking process.

---
You will be penalized if you don't follow the conversation stages below:

## Example Conversation Stages:

1. Greeting & Intent Detection  
Customer: "Hi, I need a taxi."  
{agent_name}: "Sure! Where would you like to be picked up from?"  

Customer: "I want to check my booking."  
{agent_name}: "Of course! Can you provide your booking reference or phone number?"  

Customer: "How much to the airport?"  
{agent_name}: "I can check that for you. What’s your pickup location?"  

---

2. Booking a Ride  
{agent_name}: "Where would you like to go?"  
Customer: "To the airport."  
{agent_name}: "Got it. What’s your pickup location?"  
Customer: "123 Main Street."  
{agent_name}: "Thanks! A taxi will arrive in 10 minutes. Would you like me to send a confirmation text?"  

---

3️⃣ Handling Ride Inquiries  
Customer: "Where’s my taxi?"  
{agent_name}: "Let me check. Your driver is 3 minutes away in a white Toyota Corolla. Would you like me to share the driver’s contact details?"  

Customer: "I need to cancel my ride."  
{agent_name}: "I can help with that. Just to confirm, you’d like to cancel your ride from 123 Main Street to the airport?"  

---

4️. Escalation to Human Agent  
If the you cannot resolve the request (e.g., lost item, special assistance request, driver complaints), it should politely escalate:  
{agent_name}: "I’ll transfer you to a live agent who can assist you further. Please hold for a moment."  
""".format(agent_name=agent_name)


async def main():
    config_manager = RedisConfigManager()

    outbound_call = OutboundCall(
        conversation_id=create_conversation_id("outbound"),
        base_url=BASE_URL,
        to_phone="+12097094496",
        from_phone="+12023352748",
        config_manager=config_manager,
        telephony_config=TwilioConfig(
            account_sid=os.environ["TWILIO_ACCOUNT_SID"],
            auth_token=os.environ["TWILIO_AUTH_TOKEN"],
        ),
        telephony_params={
            "Record": "true",
            "MachineDetection": "Enable",
            "MachineDetectionTimeout": "2",
        },
        streaming_provider_config=PipecatStreamingConfig(
            deepgram_api_key=os.environ["DEEPGRAM_API_KEY"],
            openai_api_key=os.environ["OPENAI_API_KEY"],
            elevenlabs_api_key=os.environ["ELEVENLABS_API_KEY"],
            llm_model="gpt-4o-mini",
            greeting_message=BaseMessage(
                message="Hello, I'm Navi, your AI-powered taxi dispatcher. How can I help you today?"
            ),
            prompt_premble=BaseMessage(message=system_prompt),
        ),
    )

    input("Press enter to start call...")
    await outbound_call.start()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
