import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from a .env file
load_dotenv()

class Settings:
    # Default to a smaller, capable model if not set in .env
    
    MODEL_URL: str = os.getenv("MODEL_URL", "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf")
    MODEL_DIR: str = os.getenv("MODEL_DIR", "model")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "mistral-7b-instruct-v0.2.Q4_K_M.gguf")
    model_path: str = os.path.join(MODEL_DIR, MODEL_NAME)

    # Sustainability API Configuration (Placeholders)
    ECOVADIS_API_KEY: Optional[str] = os.getenv("ECOVADIS_API_KEY")
    B_CORP_API_URL: Optional[str] = os.getenv("B_CORP_API_URL")
    EU_ECOLABEL_API_URL: Optional[str] = os.getenv("EU_ECOLABEL_API_URL")
    CO2_API_URL: Optional[str] = os.getenv("CO2_API_URL")

settings = Settings()