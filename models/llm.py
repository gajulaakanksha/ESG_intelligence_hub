import os
import sys

from groq import Groq

# Add parent directory to path to allow importing config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import GROQ_API_KEY, GROQ_MODEL_NAME

class GroqChatModel:
    """Minimal Groq chat wrapper to avoid pulling in torch/transformers."""

    def __init__(
        self,
        api_key: str | None,
        model: str,
        temperature: float = 0.2,
    ):
        self.model = model
        self.temperature = temperature
        self._client = Groq(api_key=api_key) if api_key else Groq()

    def invoke(self, messages: list[dict]) -> str:
        """Invoke the Groq chat completion API and return the assistant message."""
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
        )

        if resp.choices and len(resp.choices) > 0:
            return resp.choices[0].message.content or ""
        return ""


def get_chatgroq_model():
    """Initialize and return a Groq chat wrapper."""

    # Prefer the key from config, fall back to environment.
    api_key = GROQ_API_KEY or os.getenv("GROQ_API_KEY")
    if not api_key:
        return None

    try:
        if not GROQ_API_KEY:
            # Fallback to env var if config is empty
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                return None
        else:
            api_key = GROQ_API_KEY
            
        return GroqChatModel(api_key=api_key, model=GROQ_MODEL_NAME, temperature=0.2)
    except Exception as e:
        print(f"Error initializing Groq model: {str(e)}")
        return None