import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from dotenv import load_dotenv

# Define the project's root directory
BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    APP_HOST: str
    APP_PORT: int
    APP_RELOAD: bool
    APP_ENV: str = "DEV"
    APP_LOG_FILE: Path = BASE_DIR / "logs" / "app.log"
    DATA_ENCODING: str = 'utf-8'

    # LibreOffice Path (PPTX and Word conversion)
    LIBREOFFICE: str
    TMP_DIR: str

    #AI Models
    #Embedding
    KR_EMBEDDING_MODEL: str
    EN_EMBEDDING_MODEL: str
    EMBEDDING_MODEL: str

    #Inference
    LLM_MODEL: str
    MODEL_API_KEY: str

    #Vector Database Structure
    TITLE_COLUMN: str
    DATA_COLUMN: str
    DATA_VECTOR_COLUMN: str
    SUMMARY_COLUMN: str
    SUMMARY_VECTOR_COLUMN: str

    #Lexical and Semantic Search
    LEXICAL_TOP_K : int | None = 1
    SEMANTIC_TOP_K : int | None = 1
    RR_FUSION_K : int | None = 60

    #Device
    #DEVICE: str | None = "cuda" if torch.cuda.is_available() else "cpu"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
# Ensure the log directory exists
#os.makedirs(settings.APP_LOG_FILE.parent, exist_ok=True)
