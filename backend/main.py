import os
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database import (
    init_db,
    save_message,
    get_messages,
    session_exists,
    get_all_sessions,
    delete_session
)

from models import (
    ChatRequest,
    ChatResponse,
    ChatMetadata,
    HistoryResponse,
    HistoryMessage
)

from llm_service import generate_response


app = FastAPI(title="Lyftr AI Chatbot")


# =========================================================
# CORS CONFIGURATION
# =========================================================

origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# STARTUP
# =========================================================

@app.on_event("startup")
def startup():
    init_db()


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    keys = os.getenv("LLM_API_KEYS", "")

    configured_keys = [
        key.strip()
        for key in keys.split(",")
        if key.strip()
    ]

    return {
        "status": "ok",
        "keys_configured": len(configured_keys),
        "cache_enabled": True
    }


# =========================================================
# CHAT
# =========================================================

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    session_id = request.session_id
    message = request.message.strip()

    if not session_id.strip() or not message:

        return JSONResponse(
            status_code=422,
            content={
                "error": "INVALID_REQUEST",
                "message": "Message and session_id cannot be empty."
            }
        )

    try:

        # -------------------------------------------------
        # RETRIEVE PREVIOUS CONVERSATION
        # -------------------------------------------------

        previous_rows = get_messages(session_id)

        conversation_history = []

        for role, content, metadata, created_at in previous_rows:

            if role in ("user", "assistant"):

                conversation_history.append({
                    "role": role,
                    "content": content
                })

        # -------------------------------------------------
        # SAVE CURRENT USER MESSAGE
        # -------------------------------------------------

        save_message(
            session_id,
            "user",
            message
        )

        # -------------------------------------------------
        # GENERATE RESPONSE WITH CONTEXT
        # -------------------------------------------------

        result = generate_response(
            message=message,
            system_prompt=request.system_prompt,
            conversation_history=conversation_history
        )

        reply = result["reply"]

        # -------------------------------------------------
        # RESPONSE METADATA
        # -------------------------------------------------

        metadata = {
            "resolution_source": result["resolution_source"],
            "model": result["model"],
            "latency_ms": result["latency_ms"],
            "input_tokens": result["input_tokens"],
            "output_tokens": result["output_tokens"],
            "key_id": result["key_id"],
            "fallback_attempts": result["fallback_attempts"]
        }

        # -------------------------------------------------
        # SAVE ASSISTANT RESPONSE
        # -------------------------------------------------

        save_message(
            session_id,
            "assistant",
            reply,
            metadata
        )

        return ChatResponse(
            session_id=session_id,
            reply=reply,
            metadata=ChatMetadata(**metadata)
        )

    except Exception as error:

        print(f"LLM Error: {error}")

        return JSONResponse(
            status_code=503,
            content={
                "error": "AI_SERVICE_UNAVAILABLE",
                "message": (
                    "Lyftr AI is temporarily unavailable. "
                    "All configured API keys failed. "
                    "Please try again later."
                )
            }
        )


# =========================================================
# LIST ALL CHAT SESSIONS
# =========================================================

@app.get("/sessions")
def list_sessions():

    return {
        "sessions": get_all_sessions()
    }


# =========================================================
# GET MESSAGES FOR A PARTICULAR SESSION
# =========================================================

@app.get(
    "/sessions/{session_id}/messages",
    response_model=HistoryResponse
)
def get_session_history(session_id: str):

    if not session_exists(session_id):

        return JSONResponse(
            status_code=404,
            content={
                "error": "SESSION_NOT_FOUND",
                "message": "Session not found."
            }
        )

    rows = get_messages(session_id)

    messages = []

    for role, content, metadata, created_at in rows:

        parsed_metadata = None

        if metadata:
            parsed_metadata = json.loads(metadata)

        messages.append(
            HistoryMessage(
                role=role,
                content=content,
                metadata=parsed_metadata if role == "assistant" else None
            )
        )

    return {
        "session_id": session_id,
        "messages": messages
    }


# =========================================================
# DELETE A CHAT SESSION
# =========================================================

@app.delete("/sessions/{session_id}")
def remove_session(session_id: str):

    deleted = delete_session(session_id)

    if not deleted:

        return JSONResponse(
            status_code=404,
            content={
                "error": "SESSION_NOT_FOUND",
                "message": "Session not found."
            }
        )

    return {
        "message": "Chat deleted successfully.",
        "session_id": session_id
    }
