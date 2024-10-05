"""Тут модели предметной области."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class User(BaseModel):
    """Пользователь, который пишет нам сообщения."""

    id: int
    name: str | None
    full_name: str | None
    role: Literal['admin', 'user', 'anon']
    responses_today: int
    gender: bool
    last_response: datetime | None

    def is_male(self) -> bool:
        """Вернуть True если пользователь - мужчина."""
        return self.gender or self.gender is None


class Info(BaseModel):
    """Статистика."""

    responses: int
    tps: float
