from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional

# load env variables from .env file
load_dotenv()


class AgentSettings(BaseSettings):
    OPENAI_API_KEY: Optional[str] = None
    DOCUMENTS_DIR: str = "./docs_dir"
    VECTOR_STORE_DIR: str = "./doc_vector_store"
    COLLECTION_NAME: str = "documents"
    MODEL_NAME: str = "gpt-4o-mini"
    MODEL_TEMPERATURE: Optional[float] = None

    def __init__(self, **data):
        super().__init__(**data)
        if not self.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is not set. Please create a .env file in the project root with OPENAI_API_KEY=your_key_here."
            )

    def _openai_model_base_id(self) -> str:
        """Normalized OpenAI model id (no provider prefix), for LlamaIndex and CrewAI."""
        raw = (self.MODEL_NAME or "gpt-4o-mini").strip().removeprefix("openai/")
        lower = raw.lower()
        # Legacy .env from Gemini / Groq / other providers — map to a sane OpenAI default
        if "gemini" in lower or lower.startswith("llama-") or "groq" in lower:
            return "gpt-4o-mini"
        return raw if raw else "gpt-4o-mini"

    def llamaindex_openai_model(self) -> str:
        return self._openai_model_base_id()

    def crewai_openai_model(self) -> str:
        return f"openai/{self._openai_model_base_id()}"

class Config:
    env_file = ".env"
    env_file_encoding = "utf-8"
    extra = "allow"