from dotenv import load_dotenv
load_dotenv()

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.backend_src.api.chat import router as chat_router
from src.backend_src.api.documents import router as documents_router
from src.backend_src.config.backend_settings import Settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

app = FastAPI(
    title="AstraRAG API",
    description="PDF Upload, Q&A and Summarization with Agentic RAG",
    version="1.0.0"
)

# CORS_ORIGINS: comma-separated origins, or * for demos only.
_cors = os.getenv("CORS_ORIGINS", "*").strip()
_cors_list = [o.strip() for o in _cors.split(",") if o.strip()] or ["*"]
_allow_cred = "*" not in _cors_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_list,
    allow_credentials=_allow_cred,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(documents_router)

@app.get("/health")
def health_check():
    """Service liveness."""
    return {"status": "healthy", "service": "AstraRAG API"}

settings = Settings()

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", str(settings.API_PORT)))
    host = os.environ.get("API_HOST", settings.API_HOST)
    uvicorn.run(app, host=host, port=port, log_level="info")