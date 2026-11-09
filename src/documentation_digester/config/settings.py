import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel

from documentation_digester.config.paths import PATHS

load_dotenv()


class Settings(BaseModel):
    OLLAMA_BASE_URL: str
    OLLAMA_LLM_MODEL: str
    OLLAMA_EMBEDDING_MODEL: str
    CHROMA_DIRECTORY: Path = PATHS.SRC_DIRECTORY / "data" / "chroma"


settings = Settings(
    OLLAMA_BASE_URL=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    OLLAMA_LLM_MODEL=os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b"),
    OLLAMA_EMBEDDING_MODEL=os.getenv(
        "OLLAMA_EMBEDDING_MODEL",
        "nomic-embed-text:latest",
    ),
)
