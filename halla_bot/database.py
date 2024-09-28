"""Тут всё для работы с базой данных."""

from datetime import datetime
from typing import Any

import pytz
import ujson
from sqlalchemy import func
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine

from halla_bot import const
from halla_bot import db_models
from halla_bot import models


class Database:
    """Обёртка над AIOSqlite."""

    def __init__(self, db_path: str) -> None:
        """Инициализировать экземпляр."""
        self.db_path = db_path
        self.engine = create_async_engine(url=self.db_path)

    async def get_user(self, user_id: int) -> models.User:
        """Получить пользователя из базы."""
        query = select(db_models.User).where(db_models.User.id == user_id)

        async with self.engine.begin() as conn:
            response = (await conn.execute(query)).first()

            if response is None:
                user = models.User(
                    id=user_id,
                    name='',
                    full_name='',
                    role='anon',
                    responses_today=0,
                )
            else:
                user = models.User(
                    id=user_id,
                    name=response.name,
                    full_name=response.full_name,
                    role=response.role,
                    responses_today=0,
                )

            today = datetime.now().date().isoformat()

            count_query = select(func.count(db_models.Response.id)).where(
                db_models.Response.date == today,
                db_models.Response.user_id == user_id,
            )
            response = await conn.execute(count_query)
            user.responses_today = response.scalar()

        return user

    async def get_context(self, user_id: int) -> list[int] | None:
        """Получить контекст пользователя из базы."""
        query = select(db_models.Context.context).where(
            db_models.Context.user_id == user_id
        )

        async with self.engine.begin() as conn:
            response = await conn.execute(query)
            result = response.scalar()

            if result is None:
                return None

            return ujson.loads(result)

    async def store_response(
        self,
        user: models.User,
        payload: dict[str, Any],
    ) -> None:
        """Обновляем статистику для пользователя.

        Пример ответа:
        {
            'model': 'llama3.1:8B',
            'created_at': '2024-09-28T12:16:20.5298854Z',
            'response': 'Hello! How are you today?',
            'done': True,
            'done_reason':
            'stop',
            'context': [128006, 882, 128007, 271, 15339, 128009],
            'total_duration': 2989176900,
            'load_duration': 2729414000,
            'prompt_eval_count': 11,
            'prompt_eval_duration': 50352000,
            'eval_count': 24,
            'eval_duration': 197857000б
        }
        """
        _datetime = payload['created_at'][:26] + '+00:00'
        read_datetime = datetime.fromisoformat(_datetime).astimezone(
            pytz.timezone(const.CONF.timezone)
        )

        query_responses = insert(db_models.Response).values(
            user_id=user.id,
            date=read_datetime.date().isoformat(),
            time=read_datetime.time().isoformat(),
            tokens=payload['prompt_eval_count'],
            duration=payload['total_duration'] / 10**9,
        )

        query_context = insert(db_models.Context).values(
            user_id=user.id,
            context=ujson.dumps(payload['context']),
        )

        query_context = query_context.on_conflict_do_update(
            index_elements=[db_models.Context.user_id],
            set_=dict(context=query_context.excluded.context),
        )

        async with self.engine.begin() as conn:
            await conn.execute(query_responses)
            await conn.execute(query_context)

    async def get_info(self) -> models.Info:
        """Получить статистику."""
        today = datetime.now().date().isoformat()

        query = (
            select(
                func.count(),
                func.sum(db_models.Response.tokens),
                func.sum(db_models.Response.duration),
            )
            .where(db_models.Response.date == today)
            .group_by(db_models.Response.date)
        )

        async with self.engine.begin() as conn:
            response = (await conn.execute(query)).first()
            responses, total, duration = response

        return models.Info(
            responses=responses,
            tps=total / duration,
        )
