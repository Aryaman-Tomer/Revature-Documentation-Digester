#Placeholder domain for now

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from documentation_digester.domain.base import Base


class UserStory(Base):
    __tablename__ = "user_stories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    acceptance_criteria: Mapped[str] = mapped_column(Text, nullable=False)