from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional

# load env variables from .env file
load_dotenv()

class AgentSettings(BaseSettings): 
    GROQ_API_KEY: Optional[str] = None
    DOCUMENTS_DIR: str = "./docs_dir"
    VECTOR_STORE_DIR: str = "./doc_vector_store"
    COLLECTION_NAME: str = "documents"
    MODEL_NAME: Optional[str] = None
    MODEL_TEMPERATURE: Optional[float] = None

    def __init__(self, **data):
        super().__init__(**data)
        if not self.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not set. Please create a .env file in the project root with GROQ_API_KEY=your_key_here. "
                "See .env.example for configuration template."
            )

class Config:
    env_file = ".env"
    env_file_encoding = "utf-8"
    extra = "allow"