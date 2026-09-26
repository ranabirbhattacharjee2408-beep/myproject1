from companion_engine import companion_response


def ask_ai(command, conversation_context=""):
    """
    Central AI entry point.

    Provider order is handled by companion_engine:
    Gemini -> Mistral -> Cloudflare
    """
    return companion_response(
        command,
        conversation_context=conversation_context
    )
