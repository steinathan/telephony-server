# Telephony Server

> Psst! I'm looking for my next employer. If you're hiring within the VoiceAI/Agent-ish-llm space, kindly reach out to me on [LinkedIn](https://www.linkedin.com/in/navicstein). If you like my work, consider buying me a coffee at [Buy Me a Coffee](https://www.buymeacoffee.com/navicstein).

## Overview & Idea

**Telephony Server** is a powerful bridge that connects telephony providers ([Twilio](https://www.twilio.com), [Vonage](https://www.vonage.com), [Plivo](https://www.plivo.com), etc.) with real-time communication platforms ([LiveKit](https://www.livekit.io), [Jay.so](https://www.jay.so), [Pipecat](https://www.pipecat.ai), etc.). It enables seamless call routing, robust metrics collection, and observability features for enhanced telephony operations.

## Features

- **Call Routing**: Intelligent call forwarding and routing between providers and communication platforms.
- **Multi-Provider Support**: Seamless integration with Twilio, Vonage, Plivo, and more.
- **Real-time Communication**: Connects with services like LiveKit, Jay.so, and Pipecat.
- **Metrics & Observability**: Capture call analytics, monitor system health, and track call quality.
- **Scalability**: Built for high-performance and scalable architectures.
- **Webhooks & Event Handling**: Customizable event-driven architecture.

## Installation

### Prerequisites

Ensure you have the following installed:

- **Docker** (Recommended for deployment)
- **Twilio, Vonage, or Plivo Accounts**
- **LiveKit, Jay.so, or Pipecat Accounts**

### Clone the Repository

```bash
git clone https://github.com/steinathan/telephony-server.git
cd telephony-server
```

### Environment Variables

Create a `.env` file and configure your credentials:

```env
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
VONAGE_API_KEY=your_vonage_key
VONAGE_API_SECRET=your_vonage_secret
PLIVO_AUTH_ID=your_plivo_id
PLIVO_AUTH_TOKEN=your_plivo_token
LIVEKIT_API_KEY=your_livekit_key
LIVEKIT_API_SECRET=your_livekit_secret
```

### Installation Steps

```bash
uv sync
```

## Usage (Work In Progress)

Make an outbound phone call

```python
import os
from dotenv import load_dotenv


from streaming_providers.jay.jay import JayStreamingConfig
from streaming_providers.models import BaseMessage
from telephony.config_manager.redis_config_manager import RedisConfigManager
from telephony.models.telephony import TwilioConfig
from telephony.outbound_call import OutboundCall

from cuid2 import Cuid

load_dotenv()


BASE_URL = os.environ["BASE_URL"]
CUID_GENERATOR: Cuid = Cuid(length=5)


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

3️. Handling Ride Inquiries
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
        conversation_id=f"outbound_{CUID_GENERATOR.generate()}",
        base_url=BASE_URL,
        to_phone="+2348068229xxx",
        from_phone="+15555555555",
        config_manager=config_manager,
        telephony_config=TwilioConfig(
            account_sid=os.environ["TWILIO_ACCOUNT_SID"],
            auth_token=os.environ["TWILIO_AUTH_TOKEN"],
        ),
        telephony_params={
            "Record": "true",
            "MachineDetection": "Enable",
            "MachineDetectionTimeout": "5",
        },
        streaming_provider_config=JayStreamingConfig(
            agent_id="cm6icplb10002lskeiw824cfd",
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
```

```sh
$ python -m apps.telephony_app.outbound_call
```

### API Endpoints (coming soon)

#### 1. Start a Call

```http
POST /api/call/start
```

**Request Body:**

```json
{
  "provider": "twilio",
  "from": "+1234567890",
  "to": "+0987654321",
  "route_to": "livekit"
}
```

**Response:**

```json
{
  "call_id": "abc123",
  "status": "initiated"
}
```

#### 2. Get Call Metrics

```http
GET /api/call/metrics
```

**Response:**

```json
{
  "total_calls": 100,
  "active_calls": 10,
  "failed_calls": 5
}
```

## Deployment

You can deploy using Docker:

```bash
docker-compose up --build -d
```

## Observability & Monitoring

- **Prometheus & Grafana** for call metrics visualization.
- **Logging with ELK Stack (Elasticsearch, Logstash, Kibana)**.

## Contribution

We welcome contributions! Feel free to open issues and submit pull requests.

## License

MIT License

---

**Author:** Navicstein Chinemerem <br/>
**Contact:** navicsteinrotciv@gmail.com <br/>
**Linkedin:**: https://www.linkedin.com/in/navicstein <br/>
**Buy Me a Coffee:** [buymeacoffee.com/navicstein](https://www.buymeacoffee.com/navicstein)
