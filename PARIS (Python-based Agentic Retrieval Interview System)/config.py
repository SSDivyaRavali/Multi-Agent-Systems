import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent

# Document paths
UPLOAD_FOLDER = BASE_DIR /"uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

# Qdrant configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "document_embeddings"

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-3.5-turbo"

# Chunking configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO"
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "documentor_rag.log",
            "formatter": "standard",
            "level": "DEBUG"
        }
    },
    "loggers": {
        "documentor_rag": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True
        }
    }
}
