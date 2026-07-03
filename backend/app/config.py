"""
Application-wide configuration.

All values can be overridden via environment variables (see .env.example).
This keeps secrets and environment-specific paths out of source control.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings:
    # --- General ---
    APP_NAME: str = "PaperPilot AI"
    ENV: str = os.getenv("ENV", "development")

    # --- Security ---
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    # --- Database ---
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'paperpilot.db'}")

    # --- Storage ---
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    EXPORT_DIR: Path = BASE_DIR / "uploads" / "exports"
    VECTOR_STORE_DIR: Path = BASE_DIR / "data" / "vector_store"
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "25"))

    # --- AI Models (all free / local / open-source) ---
    SUMMARIZATION_MODEL: str = os.getenv("SUMMARIZATION_MODEL", "facebook/bart-large-cnn")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    QA_MODEL: str = os.getenv("QA_MODEL", "deepset/roberta-base-squad2")
    SPACY_MODEL: str = os.getenv("SPACY_MODEL", "en_core_web_sm")

    # --- Device Policy Configuration ---
    # Reads the 'DEVICE=cpu' we just added to your .env file
    DEVICE: str = os.getenv("DEVICE", "auto")

    def apply_device_policy(self):
        """
        When DEVICE=cpu, hide the GPU from PyTorch entirely by clearing
        CUDA_VISIBLE_DEVICES *before* torch is imported anywhere in the
        process.
        """
        if self.DEVICE.lower() == "cpu":
            os.environ["CUDA_VISIBLE_DEVICES"] = ""

    # --- CORS ---
    FRONTEND_ORIGINS: list = os.getenv("FRONTEND_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

    def ensure_dirs(self):
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        self.VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
        (BASE_DIR / "data").mkdir(parents=True, exist_ok=True)


settings = Settings()
# Execute device masking immediately upon importing the module configuration
settings.apply_device_policy()
settings.ensure_dirs()