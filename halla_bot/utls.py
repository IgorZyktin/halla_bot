"""Тут всякие нужные штуки."""

from typing import Awaitable
from typing import Callable
from typing import ParamSpec
from typing import TypeVar

from telegram import Update

from halla_bot import cfg

T = TypeVar('T')
P = ParamSpec('P')


def extract_user(
    function: Callable[P, Awaitable[T]],
) -> Callable[P, Awaitable[T]]:
    """Добавить пользователя в аргументы."""

    async def decorated(*args: P.args, **kwargs: P.kwargs) -> T:
        """Пойти в базу и добавить пользователя в вызов."""
        update: Update = args[0]
        user_id = int(update.message.from_user['id'])
        user = await cfg.DB.get_user(user_id)
        if user.role == 'anon':
            user.name = update.message.from_user['username'] or 'anon'
            user.full_name = update.message.from_user['username'] or 'anon'
        return await function(user, *args, **kwargs)

    return decorated
