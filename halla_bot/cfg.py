"""Тут всякие штуки, которые не меняются во время работы бота."""

from typing import Literal

from loguru import logger
from pydantic import SecretStr
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

from halla_bot import database


class Config(BaseSettings):
    """Конфигурация бота."""

    token: SecretStr
    api_url: str
    request_limit: int = 50
    request_timeout: int = 600
    prompt_limit: int = 10_000
    model: str = 'llama3.1:8B'
    mood: Literal['aggressive', 'restrictive', 'permissive'] = 'permissive'
    db_path: str = '../halla_bot.db'
    log_path: str = '../halla_bot.log'
    timezone: str = 'Europe/Moscow'

    model_config = SettingsConfigDict(
        env_prefix='HALLA_BOT__',
    )


# это считается не очень хорошей практикой т.к. инициация начнётся
# сразу во время запуска, но бот маленький, так что пофиг

CONF = Config()
logger.add(CONF.log_path, rotation='1 week')

DB = database.Database(CONF.db_path)
