#Placeholder domain for now

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from documentation_digester.domain.base import Base


class UserStory(Base):
    __tablename__ = "user_stories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    # Python attribute stays `text`; the database column is `story`.
    text: Mapped[str] = mapped_column("story", Text, nullable=False)
    acceptance_criteria: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(255), nullable=False)