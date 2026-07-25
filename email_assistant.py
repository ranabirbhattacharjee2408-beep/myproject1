import abc
import google.generativeai as genai

import speak

GEMINI_API_KEY = "AQ.Ab8RN6JVIizOwBhoHmNdGQWwLbXOw9Q8GVsIfvDdLtRv5ohtRw"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")


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
        response = model.generate_content(prompt=template)
        self.email = getattr(response, "text", str(response))
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
        response = model.generate_content(prompt=template)
        self.email = getattr(response, "text", str(response))
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