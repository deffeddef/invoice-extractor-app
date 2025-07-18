from fastapi import FastAPI
from app.api import endpoints
from app.utils.helpers import download_model
from app.config import settings
import os

app = FastAPI(
    title="Invoice Extractor API",
    description="A scalable service to accept PDF/TXT invoices, extract relevant fields using a local LLM, and return structured JSON output.",
    version="1.0.0",
)

@app.on_event("startup")
async def startup_event():
    """
    On startup, download the LLM model if it doesn't exist.
    """
    print("Checking for LLM model...")
    download_model(settings.MODEL_URL, settings.MODEL_DIR, settings.MODEL_NAME)
    
    # Create a directory for uploads if it doesn't exist
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

app.include_router(endpoints.router, prefix="/api", tags=["Invoice Extraction"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Invoice Extractor API. Go to /docs for API documentation."}