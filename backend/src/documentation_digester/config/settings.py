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

    CHROMA_DIRECTORY: Path = PATHS.ROOT_DIRECTORY / "data" / "chroma"
    SUPPORTED_EXTENSIONS: set[str] = {".txt", ".rst", ".md", ".pdf"}
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TEMPERATURE: float = 0.3


settings = Settings(
    OLLAMA_BASE_URL=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    OLLAMA_LLM_MODEL=os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b"),
    OLLAMA_EMBEDDING_MODEL=os.getenv(
        "OLLAMA_EMBEDDING_MODEL",
        "nomic-embed-text:latest",
    ),
)
