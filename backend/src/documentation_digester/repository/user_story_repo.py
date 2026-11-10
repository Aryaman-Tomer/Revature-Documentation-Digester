from sqlalchemy import select
from sqlalchemy.orm import Session

from documentation_digester.domain.user_stories import UserStory

class UserStoryRepo:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all(self) -> list[UserStory]:
        return list(self.db.scalars(select(UserStory)).all())

    def get_by_id(self, user_story_id:int) -> UserStory | None:
        return self.db.get(UserStory, user_story_id)

    def create(self, name: str) -> UserStory:
        user_story = UserStory(name=name)
        self.db.add(user_story)
        self.db.commit()
        self.db.refresh(user_story)
        return user_story

    def update(self, user_story_id: int, name: str) -> UserStory | None:
        user_story = self.get_by_id(user_story_id)
        if user_story is None:
            return None

        user_story.name = name
        self.db.commit()
        self.db.refresh(user_story)
        return user_story

    def delete(self, user_story_id: int) -> bool:
        user_story = self.get_by_id(user_story_id)
        if user_story is None:
            return False

        self.db.delete(user_story)
        self.db.commit()
        return True