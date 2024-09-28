"""Тут модели предметной области."""

from typing import Literal

from pydantic import BaseModel


class User(BaseModel):
    """Пользователь, который пишет нам сообщения."""

    id: int
    name: str | None
    full_name: str | None
    role: Literal['admin', 'user', 'anon']
    responses_today: int


class Info(BaseModel):
    """Статистика."""

    responses: int
    tps: float
