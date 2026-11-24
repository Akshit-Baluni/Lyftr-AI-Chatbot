# Lyftr AI Chatbot

A multi-turn AI chatbot built using React, FastAPI, SQLite, LiteLLM, Groq and Docker. The application supports conversational context, persistent chat sessions, response metadata, API-key fallback handling and caching.

## 1. Live URLs
Live Application: https://frontend-peach-nu-73.vercel.app/

Backend API: https://lyftr-ai-chatbot-xqno.onrender.com

Backend API Documentation (Swagger): https://lyftr-ai-chatbot-xqno.onrender.com/docs

A full-stack AI chatbot built with React, FastAPI, SQLite, Docker, and Groq-powered LLM inference. The application supports multi-turn conversations, session history, response metadata, API-key handling, and caching.

## 2. Run Locally

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker Desktop and Docker Compose
- Groq API key(s)

### Configuration

Create a `.env` file in the project root directory.

```env
LLM_MODEL=groq/openai/gpt-oss-120b
LLM_API_KEYS=your_api_key_here
```

For multiple API keys, configure them using the format supported by the backend.

Never commit real API keys to GitHub.

### Run with Docker

Build the application:

```bash
docker compose build
```

Start the application:

```bash
docker compose up -d
```

Access the application:

- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Endpoint:** http://localhost:8000/health

Stop the application:

```bash
docker compose down
```

Alternatively, use the Makefile commands:

```bash
make up
make down
```

### Run without Docker

#### Backend

Navigate to the backend directory:

```bash
cd backend
```

Create and activate a virtual environment:

```bash
python -m venv venv
```

On Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the backend:

```bash
uvicorn main:app --reload
```

#### Frontend

Open a separate terminal and navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the frontend development server:

```bash
npm run dev
```

## 3. Design Decisions

### API-Key Fallback

The application integrates an LLM through LiteLLM. Multiple API keys can be configured to support fallback handling when an API request encounters supported failures.

This improves the application's resilience to provider-related errors, including rate limits and server-side failures.

### Caching

Caching is integrated into the LLM request workflow to help reduce repeated inference requests and improve response efficiency.

Cache behavior is implemented in the backend. Cache-hit behavior is subject to verification.

### SQLite Session Storage

SQLite is used to store conversation sessions and messages.

The backend maintains session-specific conversation history, allowing the chatbot to retain context across multiple messages within a conversation.

The database is configured through the `DATABASE_URL` environment variable and stored persistently using a Docker volume.

## 4. Verification

The application supports functional verification through the frontend and backend APIs.

Verification includes:

- Sending messages and receiving AI-generated responses.
- Testing multi-turn conversations.
- Retrieving stored conversation history.
- Creating and managing chat sessions.
- Deleting conversations.
- Checking backend health through the `/health` endpoint.
- Accessing API functionality through Swagger UI.
- Running the application through Docker Compose.
- Checking per-message response metadata, including model, latency and token usage.

Fallback behavior can be tested using the failure simulation mechanism supported by the backend, including the `X-Simulate-Failure` header when failure simulation is enabled.

Cache-hit behavior and other pending verification items will be validated as part of the final testing process.

## 5. Setup Used

- **Editor:** Visual Studio Code
- **Backend:** Python, FastAPI
- **Frontend:** React, Vite
- **Database:** SQLite
- **LLM integration:** LiteLLM
- **LLM provider:** Groq
- **Containerization:** Docker and Docker Compose
- **AI assistance:** ChatGPT

## 6. Bonus Features

- Persistent conversation history.
- Conversation deletion.
- Chat session management through the frontend.
- Multi-turn contextual conversations.
- Response metadata display.
- Additional application error handling.

These features improve usability and provide a more complete conversational experience.
