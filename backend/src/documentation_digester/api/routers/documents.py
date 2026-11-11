from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from langchain_chroma import Chroma
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

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


@router.post("/ask", response_model=RagResponse)
def ask(
    request_body: PromptRequest,
    rag_service: Annotated[RagService, Depends(get_rag_service)],
):
    return rag_service.answer_from_documents(request_body.prompt)


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
def upload(
    file: Annotated[UploadFile, File(...)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
):
    try:
        return document_service.upload_document(file)
    except DocumentValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
