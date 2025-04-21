from datetime import datetime
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase

# Database classes
class Base(DeclarativeBase):
    pass


class Reaction(Base):
    __tablename__ = "reactions"
    user_id: Mapped[int] = mapped_column(String(50), primary_key=True)
    post_id: Mapped[int] = mapped_column(String(50), primary_key=True)

    def __repr__(self) -> str:
        return f"Reaction(user_id={self.user_id!r}, post_id={self.post_id!r})"


class User(Base):
    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    last_message: Mapped[datetime] = mapped_column(DateTime())

    def __repr__(self) -> str:
        return f"User(user_id={self.user_id!r}, name={self.name!r})"