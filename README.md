# Telephony Server

> This project is a prototype on how possible it is, it's heavily inspired by [Vocode](https://www.vocode.dev). If you like it, consider checking out Vocode.

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

## Usage

### API Endpoints

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

**Author:** Navicstein Chinemerem
**Contact:** navicsteinrotciv@gmail.com
