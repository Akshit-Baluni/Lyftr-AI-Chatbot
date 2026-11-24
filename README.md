# Lyftr AI Chatbot

## 1. Live URLs

- **Frontend:** `Pending deployment`
- **Backend:** `Pending deployment`
- **API Documentation:** `Pending deployment`

## 2. Run locally: with Docker and without

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker Desktop and Docker Compose
- Groq API key(s)

### Configuration

Create a `.env` file in the project root:

```env
LLM_MODEL=groq/openai/gpt-oss-120b
LLM_API_KEYS=your_api_key_here
```

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

- **Frontend:** http://localhost:5173
- **Backend:** http://localhost:8001
- **API Documentation:** http://localhost:8001/docs

Stop the application:

```bash
docker compose down
```

### Run without Docker

#### Backend

Navigate to the backend directory:

```bash
cd backend
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

Navigate to the frontend directory:

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

## 3. Design decisions: key fallback, caching, SQLite session storage

### Key fallback

The application integrates an LLM through LiteLLM. API-key configuration and fallback handling are implemented to improve resilience against provider-related failures.

The application is designed to handle API failures without disrupting the chatbot interface.

### Caching

Caching is implemented to reduce repeated LLM requests and improve response efficiency. Cached responses help reduce unnecessary API calls for repeated requests.

### SQLite session storage

SQLite is used to persist conversation sessions and messages.

The backend maintains session-specific conversation history, allowing the chatbot to retain context across multiple messages within a conversation.

The database is configured through the `DATABASE_URL` environment variable and stored persistently in the Docker environment.

## 4. Verification: how to see failover, cache hits and per-message token usage

The application is tested through functional testing of the frontend, backend, database and LLM integration.

Verification includes:

- Sending messages and receiving AI-generated responses.
- Testing multi-turn conversations.
- Retrieving stored conversation history.
- Creating new conversation sessions.
- Deleting conversations.
- Refreshing the frontend and checking conversation persistence.
- Running the application through Docker Compose.
- Checking backend health through the health endpoint.
- Checking API functionality through Swagger UI.

Cache-hit verification, failover verification through the `X-Simulate-Failure` header and per-request token usage will be demonstrated through the corresponding API and UI functionality.

## 5. Setup Used: your editor and AI tools

- **Editor:** Visual Studio Code
- **Backend:** Python, FastAPI
- **Frontend:** React, Vite
- **Database:** SQLite
- **LLM integration:** LiteLLM
- **LLM provider:** Groq
- **Containerization:** Docker and Docker Compose
- **AI assistance:** ChatGPT

## 6. Bonus features (if any): what you added beyond the requirements and why

- Persistent conversation history.
- Conversation deletion.
- Chat session management through the frontend.
- Additional application error handling.

These features improve usability and make the chatbot easier to interact with and manage.
