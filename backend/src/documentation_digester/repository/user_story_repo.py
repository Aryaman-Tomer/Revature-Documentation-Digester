from langchain_chroma import Chroma
from sqlalchemy import select
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session

from documentation_digester.domain.user_stories import UserStory
from documentation_digester.service.search_service import UserStoryHit

class UserStoryRepo:
    def __init__(self, db: Session, story_store: Chroma) -> None:
        self.db = db
        self.story_store = story_store

    def has_stories(self) -> bool:
        try:
            return self.db.scalars(select(UserStory).limit(1)).first() is not None
        except ProgrammingError:
            self.db.rollback()
            return False
            
    
    def search(self, question: str, limit: int) -> list[UserStoryHit]:
        docs = self.story_store.similarity_search(question, k=limit)
        story_ids = [int(doc.metadata["story_id"]) for doc in docs]
        stories = self.get_by_ids(story_ids)

        return [
            {
                "user_story_id" : str(story.id),
                "title" : story.title,
                "text" : story.text,
            }
            for story in stories
        ]

    def get_all(self) -> list[UserStory]:
        return list(self.db.scalars(select(UserStory)).all())

    def get_by_ids(self, ids: list[int]) -> list[UserStory]:
        if not ids:
            return []
        
        rows = self.db.scalars(select(UserStory).where(UserStory.id.in_(ids))).all()
        stories_by_id = {story.id: story for story in rows}

        return [stories_by_id[story_id] for story_id in ids if story_id in stories_by_id]

    