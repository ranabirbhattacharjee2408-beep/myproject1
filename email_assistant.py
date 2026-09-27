import abc

from config import GEMINI_API_KEY
from google import genai

client = None


def _get_client():
    global client

    if client is None:
        if not GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "Add it to your environment before using email drafting."
            )
        client = genai.Client(api_key=GEMINI_API_KEY)

    return client




class Email(abc.ABC):
    def __init__(self, subject: str = "", body: str = ""):
        self.subject = subject
        self.body = body
        self.email = ""

    @abc.abstractmethod
    def draft(self, prompt: str) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def edit(self, current_email: str, instruction: str) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, path: str = "draft.txt") -> None:
        raise NotImplementedError


class GeminiEmail(Email):
    def draft(self, prompt: str) -> str:
        template = (
            "You are an expert email writing assistant.\n\n"
            "Generate ONLY ONE email.\n\n"
            "Rules:\n"
            "- Return exactly one email.\n"
            "- Do not generate multiple versions.\n"
            "- Do not explain your choices.\n"
            "- Use the following format exactly:\n\n"
            "Subject:\n"
            "<subject>\n\n"
            "Body:\n"
            "<body>\n\n"
            "User Request:\n"
            f"{prompt}\n"
        )
        response = _get_client().models.generate_content(
         model="gemini-2.5-flash",
         contents=template
             )

        self.email = response.text
        return self.email
        
    def edit(self, current_email: str, instruction: str) -> str:
        template = (
            "You are an expert email writing assistant.\n\n"
            "Modify the email below according to the instruction.\n\n"
            "Current Email:\n"
            f"{current_email}\n\n"
            "Instruction:\n"
            f"{instruction}\n"
        )
        response = _get_client().models.generate_content(
            model="gemini-2.5-flash",
            contents=template
        )
        self.email = response.text
        return self.email

    def save(self, path: str = "draft.txt") -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.email)


def takeCommand(prompt_text: str = "Command: ") -> str:
    """Simple replacement for voice command input: read from stdin."""
    try:
        return input(prompt_text).strip()
    except Exception:
        return ""


def create_email(prompt: str) -> str:
    email_client = GeminiEmail()
    return email_client.draft(prompt)