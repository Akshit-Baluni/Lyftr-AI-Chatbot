import os
import time
import hashlib
import json

from dotenv import load_dotenv
import litellm
from litellm import completion
from litellm.caching import Cache


# =========================================================
# ENVIRONMENT CONFIGURATION
# =========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH, override=True)

MODEL = os.getenv("LLM_MODEL", "groq/openai/gpt-oss-120b")

API_KEYS = [
    key.strip()
    for key in os.getenv("LLM_API_KEYS", "").split(",")
    if key.strip()
]

print("=" * 50)
print("ENV FILE:", ENV_PATH)
print("LOADED MODEL:", MODEL)
print("API KEYS LOADED:", len(API_KEYS))
print("=" * 50)


# =========================================================
# LITELLM CACHE CONFIGURATION
# =========================================================

litellm.cache = Cache(type="local")


# =========================================================
# APPLICATION RESPONSE CACHE
# =========================================================

response_cache = {}


# =========================================================
# AI RESPONSE GENERATION
# =========================================================

def generate_response(
    message,
    system_prompt=None,
    conversation_history=None
):

    start_time = time.time()

    conversation_history = conversation_history or []

    # -----------------------------------------------------
    # MESSAGE CONSTRUCTION
    # -----------------------------------------------------

    messages = []

    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })

    # Add previous conversation context
    for history_message in conversation_history:

        role = history_message.get("role")
        content = history_message.get("content")

        if role in ("user", "assistant") and content:
            messages.append({
                "role": role,
                "content": content
            })

    # Add current user message
    messages.append({
        "role": "user",
        "content": message
    })

    # -----------------------------------------------------
    # CONTEXT-AWARE CACHE KEY
    # -----------------------------------------------------

    cache_payload = {
        "model": MODEL,
        "system_prompt": system_prompt,
        "messages": messages
    }

    cache_key = hashlib.sha256(
        json.dumps(
            cache_payload,
            sort_keys=True
        ).encode()
    ).hexdigest()

    # -----------------------------------------------------
    # CACHE CHECK
    # -----------------------------------------------------

    print("=" * 50)
    print("CACHE KEY:", cache_key)
    print("CACHE SIZE:", len(response_cache))

    if cache_key in response_cache:

        print("CACHE HIT!")

        cached_reply = response_cache[cache_key]

        return {
            "reply": cached_reply,
            "resolution_source": "LLM_CACHE",
            "model": MODEL,
            "latency_ms": int(round(
                (time.time() - start_time) * 1000
            )),
            "input_tokens": 0,
            "output_tokens": 0,
            "key_id": "CACHE",
            "fallback_attempts": 0,
        }

    print("CACHE MISS!")
    print("=" * 50)

    # -----------------------------------------------------
    # API KEY VALIDATION
    # -----------------------------------------------------

    if not API_KEYS:
        raise RuntimeError("No Groq API keys configured.")

    # -----------------------------------------------------
    # API KEY FAILOVER
    # -----------------------------------------------------

    last_error = None

    for index, api_key in enumerate(API_KEYS):

        try:

            result = completion(
                model=MODEL,
                messages=messages,
                api_key=api_key,
                temperature=0.7,
                caching=True,
            )

            reply = result.choices[0].message.content

            # -------------------------------------------------
            # SAVE RESPONSE IN APPLICATION CACHE
            # -------------------------------------------------

            response_cache[cache_key] = reply

            print("RESPONSE SAVED TO CACHE")
            print("CACHE SIZE AFTER SAVE:", len(response_cache))

            # -------------------------------------------------
            # TOKEN USAGE
            # -------------------------------------------------

            usage = result.usage

            input_tokens = (
                usage.prompt_tokens if usage else 0
            )

            output_tokens = (
                usage.completion_tokens if usage else 0
            )

            latency = int(round(
                (time.time() - start_time) * 1000
            ))

            # -------------------------------------------------
            # RETURN LIVE INFERENCE RESPONSE
            # -------------------------------------------------

            return {
                "reply": reply,
                "resolution_source": "LIVE_INFERENCE",
                "model": MODEL,
                "latency_ms": latency,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "key_id": f"KEY_{index + 1}",
                "fallback_attempts": index,
            }

        except Exception as error:

            last_error = error

            print(
                f"KEY_{index + 1} failed: {error}"
            )

    # -----------------------------------------------------
    # ALL KEYS FAILED
    # -----------------------------------------------------

    raise RuntimeError(
        f"All API keys failed: {last_error}"
    )