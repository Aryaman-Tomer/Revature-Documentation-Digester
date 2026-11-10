from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from langchain_chroma import Chroma
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, ConfigDict, Field

from documentation_digester.service.document_service import (
    DocumentService,
    DocumentValidationError,
    UploadSuccess,
)
from documentation_digester.service.rag_service import RagResponse, RagService

router = APIRouter(prefix="/documents", tags=["Documents"])


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
