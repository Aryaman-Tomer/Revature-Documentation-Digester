from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama, OllamaEmbeddings

from documentation_digester.api.routers.documents import router as documents_router
from documentation_digester.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.llm = ChatOllama(
        model=settings.OLLAMA_LLM_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=0,
        keep_alive="10m",
    )
    app.state.embeddings = OllamaEmbeddings(
        model=settings.OLLAMA_EMBEDDING_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        keep_alive=600,
    )
    app.state.chroma = Chroma(
        collection_name="documents",
        embedding_function=app.state.embeddings,
        persist_directory=str(settings.CHROMA_DIRECTORY),
    )
    app.state.story_store = Chroma(
        collection_name="user_stories",
        embedding_function=app.state.embeddings,
        persist_directory=(settings.CHROMA_DIRECTORY), 
    )

    yield

    app.state.llm = None
    app.state.embeddings = None
    app.state.chroma = None
    app.state.story_store = None


app = FastAPI(lifespan=lifespan)
app.include_router(documents_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def exception_handler(request: Request, e: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal server error: {e!s}"},
    )
