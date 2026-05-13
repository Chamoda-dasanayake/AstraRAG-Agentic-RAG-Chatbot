from dotenv import load_dotenv
load_dotenv()

import logging
from fastapi import FastAPI
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

app.include_router(chat_router)
app.include_router(documents_router)

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AstraRAG API"}

settings = Settings()

if __name__ == "__main__":
    import uvicorn

    # Run the FastAPI app when executed as a script/module.
    # Use the app object directly so output appears in the console.
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level="info",
    )