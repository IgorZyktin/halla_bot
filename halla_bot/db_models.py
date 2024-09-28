"""Тут инструменты из SQLAlchemy."""

import enum

from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    """Базовый класс всех моделей данных."""


class Role(enum.Enum):
    """Роль пользователя в системе."""

    ADMIN = 'admin'
    USER = 'user'


class User(Base):
    """Пользователь."""

    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    full_name: Mapped[str] = mapped_column(String, nullable=True)
    role: Mapped[Role] = mapped_column(String, nullable=False)


class Response(Base):
    """Данные об ответах."""

    __tablename__ = 'responses'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    date: Mapped[str] = mapped_column(String, nullable=False)
    time: Mapped[str] = mapped_column(String, nullable=False)
    tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    duration: Mapped[float] = mapped_column(Float, nullable=False)


class Context(Base):
    """Временное хранилище для метаданных сообщений."""

    __tablename__ = 'contexts'

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'), index=True, primary_key=True
    )
    context: Mapped[str] = mapped_column(String, nullable=False)
