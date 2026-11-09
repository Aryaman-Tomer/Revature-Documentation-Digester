import logging
import os
import shutil
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from langchain_chroma import Chroma
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, ConfigDict, Field

from documentation_digester.service.ingestion import (
    DocumentValidationError,
    ingest_document,
)
from documentation_digester.service.retrieval import answer_from_documents

router = APIRouter(prefix="/documents", tags=["Documents"])
logger = logging.getLogger(__name__)


class QuestionRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    question: str = Field(min_length=1, max_length=4000)


def get_vector_store(request: Request) -> Chroma:
    return request.app.state.vector_store


def get_llm_model(request: Request) -> BaseChatModel:
    return request.app.state.llm


@router.post("/chat")
def ask_documents(
    request: QuestionRequest,
    llm: BaseChatModel = Depends(get_llm_model),
    vector_store: Chroma = Depends(get_vector_store),
):
    return answer_from_documents(request.question, llm, vector_store)


@router.post("/upload")
def upload_document(
    # when working file File() the ellipsis just means a file is required
    # we could set it no None to make a file upload optional, which wouldn't make sense here
    file: UploadFile = File(...),
    vector_store: Chroma = Depends(get_vector_store),
):
    filename = os.path.basename(file.filename or "")
    extension = os.path.splitext(filename)[-1].lower()

    if not filename or extension not in {".pdf", ".txt", ".docx"}:
        raise HTTPException(
            status_code=400,
            detail="Upload a .txt, .pdf, or .docx file.",
        )

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as temp_file:
            temp_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        result = ingest_document(temp_path, filename, vector_store)

        return {"status": "success", **result}

    except DocumentValidationError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        logger.exception("Failed to ingest uploaded document %s", filename)
        raise HTTPException(
            status_code=500,
            detail="Unable to process the uploaded document.",
        ) from error

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
