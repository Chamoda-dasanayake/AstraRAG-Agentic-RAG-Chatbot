import logging
from fastapi import FastAPI
from src.backend_src.api.chat import router as chat_router
from src.backend_src.config.backend_settings import Settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

app = FastAPI()
app.include_router(chat_router)

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