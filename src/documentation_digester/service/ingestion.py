import os
import uuid

from langchain_chroma import Chroma
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentValidationError(ValueError):
    pass


def ingest_document(file_path: str, filename: str, vector_store: Chroma):
    extension = os.path.splitext(filename)[-1].lower()

    if extension == ".pdf":
        loader = PyPDFLoader(file_path)
    elif extension == ".txt":
        loader = TextLoader(file_path, encoding="utf-8")
    elif extension == ".docx":
        loader = Docx2txtLoader(file_path)
    else:
        raise DocumentValidationError("Unsupported file type")

    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True,
    )
    chunks = splitter.split_documents(documents)

    if not chunks:
        raise DocumentValidationError("The uploaded file contains no extractable text.")

    document_id = str(uuid.uuid4())
    for index, chunk in enumerate(chunks):
        chunk.metadata.update(
            {
                "document_id": document_id,
                "filename": filename,
                "chunk_index": index,
            }
        )

    vector_store.add_documents(chunks)

    return {
        "document_id": document_id,
        "filename": filename,
        "chunks_created": len(chunks),
    }
