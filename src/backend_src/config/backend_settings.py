from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings): 
    API_HOST:str = "localhost"
    API_PORT: int = 8001

    class Config:
        env_file = ".env"
        extra="allow"
