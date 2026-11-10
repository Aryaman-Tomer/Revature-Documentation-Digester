from langchain_chroma import Chroma
from typing import Protocol, TypedDict

# errors
class DocumentsNotFoundError(ValueError):
    pass

class UserStoriesNotFoundError(ValueError):
    pass


# response models FIXME: move these to /domain???
class DocumentHit(TypedDict):
    filename: str
    page: str
    chunk_index: str
    content: str

class UserStoryHit(TypedDict):
    user_story_id: str
    title: str
    text: str

class SearchResponse(TypedDict):
    documents: list[DocumentHit]
    user_stories: list[UserStoryHit]

class UserStoryRepository(Protocol):
    def has_stories(self) -> bool:
        """False if the user-story table is missing or has no rows."""
        ...

    def search(self, question: str, limit: int) -> list[UserStoryHit]:
        """Return the stories most relevant to the question."""
        ...

class SearchService:
    def __init__(self, chroma: Chroma, user_stories: UserStoryRepository):
        self.chroma = chroma
        self.user_stories = user_stories

    def search(self, question: str, k: int = 5) -> SearchResponse:
        if not self.chroma.get(limit=1)["ids"]:
            raise DocumentsNotFoundError(
                "No documentation found. Upload documents before searching."
            )

        if not self.user_stories.has_stories():
            raise UserStoriesNotFoundError(
                "No user stories found. Load user-story data before searching."
            )

        chunks = self.chroma.similarity_search(question, k=k)
        documents: list[DocumentHit] = [
            {
                "filename": chunk.metadata.get("filename", "Unknown"),
                "page": str(chunk.metadata.get("page", "N/A")),
                "chunk_index": str(chunk.metadata.get("chunk_index", "Unknown")),
                "content": chunk.page_content,
            }
            for chunk in chunks
        ]

        return {
            "documents": documents,
            "user_stories": self.user_stories.search(question, k),
        }
