from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional

load_dotenv()


class AgentSettings(BaseSettings):
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    DOCUMENTS_DIR: str = "./docs_dir"
    VECTOR_STORE_DIR: str = "./doc_vector_store"
    COLLECTION_NAME: str = "documents"
    MODEL_NAME: str = "gpt-4o-mini"
    MODEL_TEMPERATURE: Optional[float] = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.uses_gemini():
            if not (self.GOOGLE_API_KEY or "").strip():
                raise ValueError(
                    "MODEL_NAME uses Gemini. Set GOOGLE_API_KEY in .env (Google AI Studio: https://aistudio.google.com/apikey)."
                )
        elif not (self.OPENAI_API_KEY or "").strip():
            raise ValueError(
                "OPENAI_API_KEY is not set. Add it to .env, or switch MODEL_NAME to a Gemini model and set GOOGLE_API_KEY."
            )

    def uses_gemini(self) -> bool:
        return "gemini" in (self.MODEL_NAME or "").lower()

    def llm_api_key(self) -> str:
        if self.uses_gemini():
            return (self.GOOGLE_API_KEY or "").strip()
        return (self.OPENAI_API_KEY or "").strip()

    def _openai_model_base_id(self) -> str:
        """OpenAI-style model id for the LlamaIndex OpenAI LLM path (non-Gemini)."""
        raw = (self.MODEL_NAME or "gpt-4o-mini").strip().removeprefix("openai/")
        lower = raw.lower()
        if lower.startswith("llama-") or "groq" in lower:
            return "gpt-4o-mini"
        if "gemini" in lower:
            return "gpt-4o-mini"
        return raw if raw else "gpt-4o-mini"

    def llamaindex_openai_model(self) -> str:
        return self._openai_model_base_id()

    def google_genai_model_id(self) -> str:
        """Gemini model id for LlamaIndex GoogleGenAI (strip a leading `gemini/`)."""
        m = (self.MODEL_NAME or "gemini-2.0-flash").strip().removeprefix("gemini/")
        return m if m else "gemini-2.0-flash"

    def crewai_openai_model(self) -> str:
        if self.uses_gemini():
            m = (self.MODEL_NAME or "").strip()
            if not m:
                return "gemini/gemini-2.0-flash"
            return m if "/" in m else f"gemini/{m}"
        return f"openai/{self._openai_model_base_id()}"

class Config:
    env_file = ".env"
    env_file_encoding = "utf-8"
    extra = "allow"