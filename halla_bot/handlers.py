"""Тут обработчики сообщений."""

import httpx
from loguru import logger
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from halla_bot import const
from halla_bot import models
from halla_bot import utls


@utls.extract_user
async def start(
    user: models.User,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Поприветствовать пользователя."""
    logger.info('/start для {user}', user=user)

    text = (
        'Ну, привет, дружок-пирожок. Я - Галина. '
        'Могу отвечать на твои вопросы. Спроси меня что-нибудь.'
    )

    if user.role == 'anon':
        if const.CONF.mood == 'aggressive':
            text = (
                'Я знать не знаю, кто ты такой вообще. '
                'Давай, это, пойди воздухом подыши, траву потрогай. '
                'Где-нибудь не здесь.'
            )
        elif const.CONF.mood == 'restrictive':
            text = (
                'Ну, привет, дружок-пирожок. Я - Галина. '
                'Вообще то мы с тобой не знакомы. '
                'Но, так уж и быть, я готова сегодня '
                f'ответить на {const.CONF.request_limit} твоих вопросов. '
                'Спрашивай, раз пришёл.'
            )
    else:
        text = f'Привет, {user.name}! Чего тебе подсказать?'

    await update.message.reply_text(text)


@utls.extract_user
async def info(
    user: models.User,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Вернуть базовую стилистику."""
    logger.info('/info для {user}', user=user)

    _info = await const.DB.get_info()

    text = (
        f'Ответов сегодня: {_info.responses}\n'
        f'Токенов в секунду: {_info.tps:.3f}'
    )

    await update.message.reply_text(text)


@utls.extract_user
async def generate(
    user: models.User,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Ответить на вопрос пользователя."""
    logger.info('Вопрос от {user}', user=user)
    prompt = update.message.text

    if user.role == 'anon':
        if const.CONF.mood == 'aggressive':
            await update.message.reply_text(
                'Молодой человек, я вас не знаю. Уходите.'
            )
            return

        if (
            const.CONF.mood == 'restrictive'
            and user.responses_today > const.CONF.request_limit
        ):
            await update.message.reply_text(
                'Ты задаешь слишком много вопросов. '
                'Лавочка закрывается. Приходи завтра.'
            )
            return

    if len(prompt) > const.CONF.prompt_limit:
        await update.message.reply_text(
            'Ой, ну что то слишком много букв, ' 'давай покороче как-нибудь...'
        )
        return

    data = {
        'model': const.CONF.model,
        'prompt': prompt,
        'stream': False,
    }

    previous_context = await const.DB.get_context(user.id)

    if previous_context:
        data['context'] = previous_context

    # делаем вид, что бот печатает, чтобы пользователь был спокойнее
    await context.bot.send_chat_action(
        chat_id=update.message.chat_id,
        action=ChatAction.TYPING,
    )

    try:
        r = httpx.post(
            const.CONF.api_url,
            json=data,
            timeout=const.CONF.request_timeout,
        )
        payload = r.json()
    except Exception:
        logger.exception('Не удалось получить ответ от API')
        text = (
            'Ой, что-то мне нездоровится. '
            'Давай ты спросишь попозже. '
            'Через часок там, два, никогда.'
        )
        await update.message.reply_text(text)
        return

    await const.DB.store_response(user, payload)
    await update.message.reply_text(payload['response'])
