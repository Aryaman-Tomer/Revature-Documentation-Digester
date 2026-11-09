import os

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):
    OLLAMA_BASE_URL: str
    OLLAMA_LLM_MODEL: str
    OLLAMA_EMBEDDING_MODEL: str = "qwen3-embedding:0.6b"
    CHROMA_DIRECTORY: str = "./data/chroma"


settings = Settings(
    OLLAMA_BASE_URL=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    OLLAMA_LLM_MODEL=os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b"),
    OLLAMA_EMBEDDING_MODEL=os.getenv(
        "OLLAMA_EMBEDDING_MODEL",
        "nomic-embed-text:latest",
    ),
)
