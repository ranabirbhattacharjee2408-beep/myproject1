import os
import time
import requests

from google import genai
from mistralai.client import Mistral

from config import (
    GEMINI_API_KEY,
    MISTRAL_API_KEY,
    CLOUDFLARE_ACCOUNT_ID,
    CLOUDFLARE_API_TOKEN,
)


# ============================================================
# JARVIS COMPANION ENGINE
# ============================================================
#
# AI FALLBACK CHAIN:
#
#   1. Gemini 2.5 Flash
#          ↓
#   2. Mistral Ministral 8B
#          ↓
#   3. Cloudflare Workers AI
#
# Ollama is intentionally NOT used for now.
#
# API keys are loaded from:
# D:\JARVIS\.env
#
# ============================================================



# ============================================================
# MODEL CONFIGURATION
# ============================================================

GEMINI_MODEL = "gemini-3.6-flash"

MISTRAL_MODEL = "ministral-8b-2512"

CLOUDFLARE_MODEL = "@cf/meta/llama-3.1-8b-instruct"


# ============================================================
# RETRY / TIMEOUT CONFIGURATION
# ============================================================

# Number of attempts for temporary provider failures.
MAX_RETRIES = 2

# Delay between retry attempts.
RETRY_DELAY = 1.5

# Cloudflare HTTP timeout.
CLOUDFLARE_TIMEOUT = 30


# ============================================================
# AI CLIENTS
# ============================================================

gemini_client = None
mistral_client = None


if GEMINI_API_KEY:
    gemini_client = genai.Client(
        api_key=GEMINI_API_KEY
    )


if MISTRAL_API_KEY:
    mistral_client = Mistral(
        api_key=MISTRAL_API_KEY
    )


# ============================================================
# MEMORY / CHAT FORMATTING
# ============================================================

def format_memories(memories):
    """
    Format stored memories into readable text.
    """

    if not memories:
        return "No relevant memories."

    return "\n".join(
        f"- {memory}"
        for memory in memories
    )


def format_chat(recent_chat):
    """
    Format recent conversation history.
    """

    if not recent_chat:
        return "No recent conversation."

    return "\n".join(
        f"{msg['role']}: {msg['content']}"
        for msg in recent_chat
    )


# ============================================================
# PROMPT BUILDER
# ============================================================

class Prompt:
    """
    Prompt builder for the JARVIS companion engine.
    """

    def format_memories(self, memories):
        return format_memories(memories)

    def format_chat(self, recent_chat):
        return format_chat(recent_chat)

    def build(self, user_message, context):

        context = context or {}

        emotion = context.get(
            "emotion",
            "neutral"
        )

        memories = self.format_memories(
            context.get(
                "memories",
                []
            )
        )

        recent_chat = self.format_chat(
            context.get(
                "recent_chat",
                []
            )
        )

        return f"""
You are JARVIS, the user's long-term virtual companion
and AI assistant.

Your personality is:

- calm
- intelligent
- warm
- observant
- confident
- naturally witty when appropriate
- emotionally aware

CURRENT CONTEXT:
{context}

RELEVANT MEMORIES:
{memories}

CURRENT USER STATE:
{emotion}

RECENT CONVERSATION:
{recent_chat}

CURRENT USER MESSAGE:
{user_message}

Respond naturally to the user's latest message.
"""


def build_prompt(user_message, context):
    """
    Build a JARVIS prompt.
    """

    return Prompt().build(
        user_message,
        context
    )


# ============================================================
# GEMINI
# ============================================================

def ask_gemini(prompt):

    if not gemini_client:

        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    print(
        "[COMPANION] Trying Gemini..."
    )

    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    reply = response.text

    if not reply or not reply.strip():

        raise RuntimeError(
            "Gemini returned an empty response."
        )

    print(
        "[COMPANION] Gemini response received."
    )

    return reply.strip()


# ============================================================
# MISTRAL
# ============================================================

def ask_mistral(prompt):

    if not mistral_client:

        raise RuntimeError(
            "MISTRAL_API_KEY is not configured."
        )

    print(
        "[COMPANION] Switching to Mistral..."
    )

    response = mistral_client.chat.complete(

        model=MISTRAL_MODEL,

        messages=[

            {
                "role": "system",

                "content": (
                    "You are JARVIS, an intelligent "
                    "personal AI assistant. "
                    "You are calm, helpful, natural, "
                    "concise, confident, and conversational."
                )
            },

            {
                "role": "user",

                "content": prompt
            }

        ]
    )

    reply = response.choices[0].message.content

    if not reply or not reply.strip():

        raise RuntimeError(
            "Mistral returned an empty response."
        )

    print(
        "[COMPANION] Mistral response received."
    )

    return reply.strip()


# ============================================================
# CLOUDFLARE WORKERS AI
# ============================================================

def ask_cloudflare(prompt):

    if not CLOUDFLARE_ACCOUNT_ID:

        raise RuntimeError(
            "CLOUDFLARE_ACCOUNT_ID is not configured."
        )

    if not CLOUDFLARE_API_TOKEN:

        raise RuntimeError(
            "CLOUDFLARE_API_TOKEN is not configured."
        )

    print(
        "[COMPANION] Switching to Cloudflare..."
    )

    url = (
        "https://api.cloudflare.com/client/v4/"
        f"accounts/{CLOUDFLARE_ACCOUNT_ID}/"
        f"ai/run/{CLOUDFLARE_MODEL}"
    )

    headers = {

        "Authorization":
            f"Bearer {CLOUDFLARE_API_TOKEN}",

        "Content-Type":
            "application/json"
    }

    data = {

        "messages": [

            {
                "role": "system",

                "content": (
                    "You are JARVIS, an intelligent "
                    "personal AI assistant. "
                    "You are calm, helpful, natural, "
                    "concise, confident, and conversational."
                )
            },

            {
                "role": "user",

                "content": prompt
            }

        ]
    }

    response = requests.post(

        url,

        headers=headers,

        json=data,

        timeout=CLOUDFLARE_TIMEOUT
    )

    if not response.ok:

        raise RuntimeError(
            f"Cloudflare HTTP "
            f"{response.status_code}: "
            f"{response.text}"
        )

    result = response.json()

    if not result.get("success"):

        raise RuntimeError(
            f"Cloudflare request failed: "
            f"{result}"
        )

    reply = (
        result
        .get("result", {})
        .get("response")
    )

    if not reply or not reply.strip():

        raise RuntimeError(
            "Cloudflare returned an empty response."
        )

    print(
        "[COMPANION] Cloudflare response received."
    )

    return reply.strip()


# ============================================================
# PROVIDER RETRY HELPER
# ============================================================

def call_with_retry(
    provider_name,
    provider_function,
    prompt
):
    """
    Try a provider more than once before
    allowing the fallback chain to continue.
    """

    last_error = None

    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        try:

            if attempt > 1:

                print(
                    f"[COMPANION] Retrying "
                    f"{provider_name} "
                    f"({attempt}/{MAX_RETRIES})..."
                )

                time.sleep(
                    RETRY_DELAY
                )

            return provider_function(
                prompt
            )

        except Exception as error:

            last_error = error

            print(
                f"[COMPANION] "
                f"{provider_name} attempt "
                f"{attempt} failed."
            )

            print(
                f"[COMPANION] Error: "
                f"{repr(error)}"
            )

    raise RuntimeError(
        f"{provider_name} failed after "
        f"{MAX_RETRIES} attempts: "
        f"{repr(last_error)}"
    )


# ============================================================
# MAIN COMPANION ENGINE
# ============================================================

def companion_response(
    command,
    conversation_context=""
):

    print(
        f"[COMPANION] Processing: {command}"
    )


    # ========================================================
    # MAIN JARVIS PROMPT
    # ========================================================

    prompt = f"""
You are JARVIS, an intelligent personal AI assistant.

You are having an ongoing natural conversation
with the user.

==================================================
RECENT CONVERSATION
==================================================

{conversation_context}

==================================================
CURRENT USER MESSAGE
==================================================

{command}

==================================================
CONVERSATION RULES
==================================================

1. Use the recent conversation to understand
   the user's meaning.

2. Resolve references naturally.

For example:

User: Who is Mark Zuckerberg?

Jarvis: Mark Zuckerberg is the founder of Facebook.

User: How many apps does he own?

Understand that "he" refers to Mark Zuckerberg.

3. Understand references such as:

- he
- she
- they
- it
- this
- that
- these
- those
- the first one
- the second one
- his
- her
- their
- there
- the company
- the person
- the app
- the previous one

using the conversation context.

4. Do NOT ask who the user means if
   the previous conversation makes the meaning clear.

5. Continue the conversation naturally.

6. If the user previously provided information
   about themselves, use it when relevant.

7. If the user asks "what is my name?"
   and their name appears in the conversation
   context, answer using that name.

8. Do not claim that you have forgotten something
   when the answer can reasonably be determined
   from the conversation context.

9. Do not repeat the entire conversation.

10. Answer the CURRENT USER MESSAGE directly.

11. Keep normal answers concise unless the
    user asks for detail.

12. You are JARVIS.

Respond naturally, intelligently,
and confidently.

==================================================
ANSWER
==================================================
"""


    print(
        "[COMPANION DEBUG] Prompt length:",
        len(prompt)
    )


    if not prompt.strip():

        raise ValueError(
            "Generated prompt is empty!"
        )


    # ========================================================
    # PROVIDER 1 — GEMINI
    # ========================================================

    try:

        return call_with_retry(
            "Gemini",
            ask_gemini,
            prompt
        )

    except Exception as gemini_error:

        print(
            "[COMPANION] Gemini failed."
        )

        print(
            "[COMPANION] Gemini final error:",
            repr(gemini_error)
        )


    # ========================================================
    # PROVIDER 2 — MISTRAL
    # ========================================================

    try:

        return call_with_retry(
            "Mistral",
            ask_mistral,
            prompt
        )

    except Exception as mistral_error:

        print(
            "[COMPANION] Mistral failed."
        )

        print(
            "[COMPANION] Mistral final error:",
            repr(mistral_error)
        )


    # ========================================================
    # PROVIDER 3 — CLOUDFLARE
    # ========================================================

    try:

        return call_with_retry(
            "Cloudflare",
            ask_cloudflare,
            prompt
        )

    except Exception as cloudflare_error:

        print(
            "[COMPANION] Cloudflare failed."
        )

        print(
            "[COMPANION] Cloudflare final error:",
            repr(cloudflare_error)
        )


    # ========================================================
    # ALL PROVIDERS FAILED
    # ========================================================

    return (
        "I'm unable to connect to my AI engines "
        "right now. Please check your internet "
        "connection or AI service configuration."
    )


# ============================================================
# OPTIONAL DIRECT TEST
# ============================================================

if __name__ == "__main__":

    print(
        "\n=============================================="
    )

    print(
        "        JARVIS COMPANION ENGINE TEST"
    )

    print(
        "==============================================\n"
    )

    result = companion_response(
        "Say hello in one short sentence."
    )

    print("\nJARVIS:")
    print(result)

    print(
        "\n=============================================="
    )
def companion_route(command, conversation_context=""):
    """
    Decide whether the user's request is a JARVIS command or normal chat.

    Returns:
        {"type": "command", "command": "..."}
        {"type": "chat", "response": "..."}
    """

    router_prompt = f"""
You are JARVIS's command router.

Recent conversation history:
{conversation_context}

Current user request:
{command}

Classify the request into exactly ONE of these:

COMMAND:
Use COMMAND when JARVIS needs to perform an action, such as:
- open/launch/start an application
- open a website
- search the web
- search YouTube
- play music
- create a reminder
- add something to the calendar
- shutdown/restart/lock the computer
- enter conversation mode
- enter writing mode

For COMMAND, return:
{{"type":"command","command":"the actual canonical command"}}

Example:
User request: open youtube
Output:
{{"type":"command","command":"open youtube"}}

CHAT:
Use CHAT for normal questions, facts, explanations, conversation, or anything that does not require a computer action.

For CHAT, you MUST answer the user's question yourself.

Return:
{{"type":"chat","response":"the actual answer to the user's request"}}

IMPORTANT:
- NEVER use placeholder text.
- NEVER write "answer here".
- NEVER write "actual answer".
- NEVER write "response here".
- NEVER write "CANONICAL COMMAND".
- The response field must contain the actual answer.
- Return ONLY valid JSON.
- Do not use markdown.
- Do not add anything outside the JSON.

Recent conversation history:
{conversation_context}

Current user request:
{command}
"""

    print("[ROUTER] Understanding request...")

    try:
        raw_response = call_with_retry(
            "Gemini",
            ask_gemini,
            router_prompt
        )

        if not raw_response:
            raise RuntimeError("Router returned an empty response.")

        print("[ROUTER RAW]", raw_response)

        import json
        import re

        cleaned = raw_response.strip()

        # Remove markdown code fences if Gemini adds them.
        cleaned = re.sub(
            r"^```json\s*",
            "",
            cleaned,
            flags=re.IGNORECASE
        )
        cleaned = re.sub(
            r"^```\s*",
            "",
            cleaned
        )
        cleaned = re.sub(
            r"\s*```$",
            "",
            cleaned
        )

        cleaned = cleaned.strip()

        # Find the first JSON object.
        match = re.search(
            r'\{.*\}',
            cleaned,
            re.DOTALL
        )

        if not match:
            raise ValueError(
                "Router did not return a JSON object."
            )

        route = json.loads(match.group(0))

        if not isinstance(route, dict):
            raise ValueError(
                "Router result is not a dictionary."
            )

        route_type = str(
            route.get("type", "")
        ).lower().strip()

        # -------------------------
        # COMMAND
        # -------------------------

        if route_type == "command":

            routed_command = str(
                route.get("command", "")
            ).strip()

            invalid_commands = {
                "",
                "canonical command",
                "the actual canonical command"
            }

            if routed_command.lower() in invalid_commands:
                raise ValueError(
                    "Router returned an invalid command."
                )

            print(
                "[ROUTER] COMMAND:",
                routed_command
            )

            return {
                "type": "command",
                "command": routed_command
            }

        # -------------------------
        # CHAT
        # -------------------------

        if route_type == "chat":

            response = str(
                route.get("response", "")
            ).strip()

            invalid_placeholders = {
                "",
                "answer here",
                "actual answer",
                "response here",
                "your answer here",
                "the actual answer",
                "the actual answer to the user's request",
                "answer",
                "response"
            }

            if response.lower() in invalid_placeholders:
                raise ValueError(
                    "Router returned a placeholder chat response."
                )

            print("[ROUTER] CHAT")

            return {
                "type": "chat",
                "response": response
            }

        raise ValueError(
            f"Unknown router type: {route_type}"
        )

    except Exception as error:

        print(
            "[ROUTER ERROR]",
            repr(error)
        )

        # Never allow the router failure to reach the user.
        # Use the normal companion engine as the fallback.

        print(
            "[ROUTER] Falling back to companion response..."
        )

        response = companion_response(
            command,
            conversation_context=conversation_context
        )

        return {
            "type": "chat",
            "response": response
        }

