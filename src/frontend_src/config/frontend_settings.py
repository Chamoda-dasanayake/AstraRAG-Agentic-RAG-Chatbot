from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings): 
    CHAT_ENDPOINT_URL: str = "http://localhost:8001/chat/answer"

class Config: 
    env_file = ".env"
    extra="allow"