import os
import shutil
import tempfile
import uuid
from typing import Any, Protocol, TypedDict

from fastapi import UploadFile
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document

from documentation_digester.config.settings import settings


class DocumentValidationError(ValueError):
    pass


class UploadSuccess(TypedDict):
    document_id: str
    filename: str
    chunks_created: int


class ChunkerProtocol(Protocol):
    def split_documents(self, documents: list[Document]) -> list[Document]: ...


class DocumentService:
    def __init__(self, chroma: Chroma, chunker: ChunkerProtocol):
        self.chroma = chroma
        self.chunker = chunker

    def delete_file(self, file_name: str) -> bool:
        result = self.chroma.get(where={"filename": file_name})
        document_ids = result.get("ids", [])

        if document_ids:
            self.chroma.delete(ids=document_ids)
            return True
        else:
            return False

    def get_all_files(self) -> set[str]:
        metadatas = self.chroma.get(include=["metadatas"])["metadatas"]
        unique_files = {m["filename"] for m in metadatas}
        return unique_files

    def get_all_chunks(self, truncate: int) -> list[dict[str, Any]]:
        data = self.chroma.get(include=["documents", "metadatas"])
        documents = data["documents"]
        metadatas = data["metadatas"]
        result = [
            {
                "filename": metadata["filename"],
                "chunk_index": metadata["chunk_index"],
                "start_index": metadata["start_index"],
                "content_length": len(document),
                "content": f"{document[:truncate]}..."
                if len(document) > truncate
                else document,
            }
            for document, metadata in zip(documents, metadatas)
        ]
        return result

    def upload_document(self, file: UploadFile) -> UploadSuccess:
        filename = os.path.basename(file.filename or "")
        extension = os.path.splitext(filename)[-1].lower()

        if not filename or extension not in settings.SUPPORTED_EXTENSIONS:
            raise DocumentValidationError(
                f"File must be one of {settings.SUPPORTED_EXTENSIONS}"
            )

        temp_path: str | None = None

        try:
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=extension
            ) as temp_file:
                temp_path = temp_file.name
                shutil.copyfileobj(file.file, temp_file)

            match extension:
                case ".txt" | ".rst" | ".md":
                    loader = TextLoader(temp_path, encoding="utf-8")
                case ".pdf":
                    loader = PyPDFLoader(temp_path)
                case _:
                    raise DocumentValidationError(
                        f"File must be one of {settings.SUPPORTED_EXTENSIONS}"
                    )

            document = loader.load()
            chunks = self.chunker.split_documents(document)

            if not chunks:
                raise DocumentValidationError(
                    "The uploaded file contains no extractable text."
                )

            document_id = str(uuid.uuid4())
            for index, chunk in enumerate(chunks):
                chunk.metadata.update(
                    {
                        "document_id": document_id,
                        "filename": filename,
                        "chunk_index": index,
                    }
                )

            self.chroma.add_documents(chunks)

            return {
                "document_id": document_id,
                "filename": filename,
                "chunks_created": len(chunks),
            }

        except Exception as e:
            raise DocumentValidationError(
                f"Failed to process document {filename}: {e!s}"
            ) from e

        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
