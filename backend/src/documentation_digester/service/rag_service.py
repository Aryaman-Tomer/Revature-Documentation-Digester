import json
from typing import TypedDict

from langchain_chroma import Chroma
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)


class RagResponse(TypedDict):
    response: str
    sources: list[dict[str, str]]


class RagService:
    NO_CONTEXT_FALLBACK = "I don't have enough information from the provided documents to answer this prompt."

    def __init__(self, llm: BaseChatModel, chroma: Chroma):
        self.llm = llm
        self.chroma = chroma
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template("""
                    You are a strict QA assistant.
                    Answer the user's question using ONLY the provided Document Context below.

                    Rules:
                    1. Do NOT use any prior knowledge outside of the provided context.
                    2. If the answer cannot be directly derived from the provided context, respond EXACTLY with:
                    "{fallback_text}"
                    3. Do not attempt to explain why or add conversational text if the context is insufficient."""),
                HumanMessagePromptTemplate.from_template("""
                    Document Context:
                    {context}

                    User Prompt:
                    {prompt}
                """),
            ]
        )
        self.chain = self.prompt_template | self.llm | StrOutputParser()

    def answer_from_documents(self, prompt: str, k: int = 5) -> RagResponse:
        retrieved_chunks = self.chroma.similarity_search(prompt, k=k)
        transformed_chunks = [
            {
                "filename": chunk.metadata.get("filename", "Unknown"),
                "page": str(chunk.metadata.get("page", "N/A")),
                "chunk_index": str(chunk.metadata.get("chunk_index", "Unknown")),
                "content": chunk.page_content,
            }
            for chunk in retrieved_chunks
        ]

        if not retrieved_chunks:
            return {
                "response": self.NO_CONTEXT_FALLBACK,
                "sources": [],
            }

        context = "\n---\n".join(json.dumps(chunk) for chunk in transformed_chunks)
        answer = self.chain.invoke(
            {
                "context": context,
                "prompt": prompt,
                "fallback_text": self.NO_CONTEXT_FALLBACK,
            }
        )

        return {
            "response": answer,
            "sources": transformed_chunks,
        }
