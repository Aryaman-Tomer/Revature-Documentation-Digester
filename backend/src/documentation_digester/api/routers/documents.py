from typing import Annotated

from collections.abc import AsyncIterable

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.sse import EventSourceResponse, ServerSentEvent
from langchain_chroma import Chroma
from langchain_core.language_models import BaseChatModel
from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session


from documentation_digester.db.database import get_db
from documentation_digester.repository.user_story_repo import UserStoryRepo
from documentation_digester.config.settings import settings

from documentation_digester.service.document_service import (
    ChunkerProtocol,
    DocumentService,
    DocumentValidationError,
    UploadSuccess,
)
from documentation_digester.service.rag_service import RagResponse, RagService
from documentation_digester.service.search_service import (
    DocumentsNotFoundError,
    SearchResponse,
    SearchService,
    UserStoriesNotFoundError,
    UserStoryRepository,
)

router = APIRouter(prefix="/documents", tags=["Documents"])

class SearchRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    question: str = Field(min_length=1, max_length=1000)
    k: int = Field(default=5, ge=1)

class PromptRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    prompt: str = Field(min_length=1, max_length=1000)


def get_chroma(request: Request) -> Chroma:
    return request.app.state.chroma


def get_chunker(request: Request) -> ChunkerProtocol:
    if settings.CHUNKING_STRATEGY == "text_splitter":
        return RecursiveCharacterTextSplitter(
            chunk_size=settings.TEXT_SPLITTER_CHUNK_SIZE,
            chunk_overlap=settings.TEXT_SPLITTER_CHUNK_OVERLAP,
            add_start_index=True,
        )
    elif settings.CHUNKING_STRATEGY == "semantic":
        return SemanticChunker(
            embeddings=request.app.state.embeddings,
            breakpoint_threshold_type="percentile",
            breakpoint_threshold_amount=settings.SEMANTIC_CHUNKER_BREAKPOINT_THRESHOLD,
            add_start_index=True,
        )
    else:
        raise ValueError(f"Invalid chunking strategy: {settings.CHUNKING_STRATEGY}.")


def get_llm_model(request: Request) -> BaseChatModel:
    return request.app.state.llm


def get_rag_service(
    llm: Annotated[BaseChatModel, Depends(get_llm_model)],
    chroma: Annotated[Chroma, Depends(get_chroma)],
) -> RagService:
    return RagService(llm, chroma)


def get_document_service(
    chroma: Annotated[Chroma, Depends(get_chroma)],
    chunker: Annotated[ChunkerProtocol, Depends(get_chunker)],
) -> DocumentService:
    return DocumentService(chroma, chunker)


def get_story_store(request: Request) -> Chroma:
    return request.app.state.story_store


def get_user_story_repo(
    db: Session = Depends(get_db),
    story_store: Chroma = Depends(get_story_store),
) -> UserStoryRepository:
    return UserStoryRepo(db, story_store)


def get_search_service(
    chroma: Annotated[Chroma, Depends(get_chroma)],
    user_stories: Annotated[UserStoryRepository, Depends(get_user_story_repo)],
) -> SearchService:
    return SearchService(chroma=chroma, user_stories=user_stories)


@router.get("/names")
def get_all_uploaded_document_names(
    document_service: Annotated[DocumentService, Depends(get_document_service)],
):
    return document_service.get_all_files()


@router.get("/chunks")
def get_all_chunks(
    document_service: Annotated[DocumentService, Depends(get_document_service)],
    truncate: int = 50,
):
    return document_service.get_all_chunks(truncate)


@router.post("/ask", response_model=RagResponse)
def ask_questions_about_existing_documents(
    request_body: PromptRequest,
    rag_service: Annotated[RagService, Depends(get_rag_service)],
):
    return rag_service.answer_from_documents(request_body.prompt)


@router.post("/ask/stream", response_class=EventSourceResponse)
async def stream_answer_about_existing_documents(
    request_body: PromptRequest,
    rag_service: Annotated[RagService, Depends(get_rag_service)],
) -> AsyncIterable[ServerSentEvent]:
    async for event, data in rag_service.stream_answer_from_documents(request_body.prompt):
        yield ServerSentEvent(data=data, event=event)


@router.post("/search", response_model=SearchResponse)
def search(
    request_body: SearchRequest,
    search_service: Annotated[SearchService, Depends(get_search_service)],
):
    try:
        return search_service.search(request_body.question, request_body.k)
    except (DocumentsNotFoundError, UserStoriesNotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/upload", response_model=UploadSuccess)
def upload_a_document(
    file: Annotated[UploadFile, File(...)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
):
    try:
        return document_service.upload_document(file)
    except DocumentValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{file_name}")
def delete_an_uploaded_document(
    file_name: str,
    document_service: Annotated[DocumentService, Depends(get_document_service)],
):
    return document_service.delete_file(file_name)
