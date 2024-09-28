"""Отсюда начинается исполнение кода."""

from loguru import logger
from telegram import Update
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import filters

from halla_bot import const
from halla_bot import handlers


def main() -> None:
    """Точка входа."""
    logger.warning('Бот начал работу')
    token = const.CONF.token.get_secret_value()
    application = Application.builder().token(token).build()

    start_handler = CommandHandler('start', handlers.start)
    info_handler = CommandHandler('info', handlers.info)
    gen_handler = MessageHandler(
        filters.TEXT & (~filters.COMMAND),
        handlers.generate,
    )

    application.add_handler(start_handler)
    application.add_handler(info_handler)
    application.add_handler(gen_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)
    logger.warning('Бот закончил работу')


if __name__ == '__main__':
    main()
