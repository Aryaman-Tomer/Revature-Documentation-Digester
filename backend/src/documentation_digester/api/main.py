from contextlib import ExitStack, asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama, OllamaEmbeddings
from sqlalchemy.engine import make_url
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.store.postgres import PostgresStore

from documentation_digester.api.routers.documents import router as documents_router
from documentation_digester.api.routers.user_stories import router as user_stories_router
from documentation_digester.config.settings import settings
from documentation_digester.service.memory import build_memory_graph


def _langgraph_database_url(database_url: str) -> str:
    url = make_url(database_url)
    if url.drivername.startswith("postgresql+"):
        url = url.set(drivername="postgresql")
    return url.render_as_string(hide_password=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.llm = ChatOllama(
        model=settings.OLLAMA_LLM_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=settings.TEMPERATURE,
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
        persist_directory=str(settings.CHROMA_DIRECTORY), 
    )

    database_url = _langgraph_database_url(settings.DATABASE_URL)
    # Keep both PostgreSQL context managers open while the app is serving
    # requests. ExitStack lets us enter multiple resources in one block and
    # closes them in reverse order after shutdown (or if startup raises).
    with ExitStack() as resources:
       
        checkpoint_connection = resources.enter_context(
            PostgresSaver.from_conn_string(database_url)
        )
        checkpoint_connection.serde = JsonPlusSerializer(
            allowed_msgpack_modules=[
                ("langchain_core.messages.human", "HumanMessage"),
                ("langchain_core.messages.ai", "AIMessage"),
            ]
        )
        # LangGraph creates and migrates its checkpoint tables.
        checkpoint_connection.setup()

        memory_store = resources.enter_context(
            PostgresStore.from_conn_string(database_url)
        )
        # LangGraph creates and migrates its store tables.
        memory_store.setup()

        app.state.memory_store = memory_store
        app.state.memory_graph = build_memory_graph(
            app.state.llm,
            checkpoint_connection,
            memory_store,
        )
        # Yield control to FastAPI; the resources above remain open throughout
        # the serving period and are closed when the lifespan resumes at shutdown.
        yield

    app.state.llm = None
    app.state.embeddings = None
    app.state.chroma = None
    app.state.story_store = None
    app.state.memory_graph = None
    app.state.memory_store = None


app = FastAPI(lifespan=lifespan)
app.include_router(documents_router)
app.include_router(user_stories_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def exception_handler(request: Request, e: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal server error: {e!s}"},
    )
