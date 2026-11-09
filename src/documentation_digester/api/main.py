from contextlib import asynccontextmanager

from fastapi import FastAPI
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama, OllamaEmbeddings

from documentation_digester.api.routers.documents import router as documents_router
from documentation_digester.api.routers.test import router as test_router
from documentation_digester.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.llm = ChatOllama(
        model=settings.OLLAMA_LLM_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=0,
        keep_alive="30m",
    )
    app.state.embeddings = OllamaEmbeddings(
        model=settings.OLLAMA_EMBEDDING_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        keep_alive=1800,
    )
    app.state.vector_store = Chroma(
        collection_name="documents",
        embedding_function=app.state.embeddings,
        persist_directory=str(settings.CHROMA_DIRECTORY),
    )

    yield

    app.state.llm = None
    app.state.embeddings = None
    app.state.vector_store = None


app = FastAPI(lifespan=lifespan)

app.include_router(test_router)
app.include_router(documents_router)
