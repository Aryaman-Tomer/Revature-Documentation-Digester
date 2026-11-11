from typing import Annotated

from collections.abc import AsyncIterable

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.sse import EventSourceResponse, ServerSentEvent
from langchain_chroma import Chroma
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from documentation_digester.db.database import get_db
from documentation_digester.repository.user_story_repo import UserStoryRepo
from documentation_digester.service.document_service import (
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


def get_llm_model(request: Request) -> BaseChatModel:
    return request.app.state.llm


def get_rag_service(
    llm: Annotated[BaseChatModel, Depends(get_llm_model)],
    chroma: Annotated[Chroma, Depends(get_chroma)],
) -> RagService:
    return RagService(llm, chroma)


def get_document_service(
    chroma: Annotated[Chroma, Depends(get_chroma)],
) -> DocumentService:
    return DocumentService(chroma=chroma)


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


@router.get("/")
def get_all_uploaded_document_names(
    document_service: Annotated[DocumentService, Depends(get_document_service)],
):
    return document_service.get_all_files()


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
