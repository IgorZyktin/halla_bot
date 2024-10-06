"""Тут обработчики сообщений."""

from datetime import datetime

import httpx
from loguru import logger
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from halla_bot import cfg
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

    if user.role == 'anon':
        if cfg.CONF.mood == 'aggressive':
            text = (
                'Я знать не знаю, кто ты такой вообще. '
                'Давай, это, пойди воздухом подыши, траву потрогай. '
                'Где-нибудь не здесь.'
            )
        elif cfg.CONF.mood == 'restrictive':
            text = (
                'Ну, привет, дружок-пирожок. Я - Галина. '
                'Вообще то мы с тобой не знакомы. '
                'Но, так уж и быть, я готова сегодня '
                f'ответить на {cfg.CONF.request_limit} твоих вопросов. '
                'Спрашивай, раз пришёл.'
            )
        else:
            text = (
                'Ну, привет, дружок-пирожок. Я - Галина. '
                'Могу отвечать на твои вопросы. Спроси меня что-нибудь.'
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

    _info = await cfg.DB.get_info()

    text = (
        f'Текущая модель: {cfg.CONF.model}\n'
        f'Настрой бота: {cfg.CONF.mood}\n'
        f'Ответов сегодня: {_info.responses}\n'
        f'Токенов в секунду: {_info.tps:.3f}'
    )

    await update.message.reply_text(text, reply_markup=None)


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
        if cfg.CONF.mood == 'aggressive':
            # анонимус по умолчанию считается мужчиной
            await update.message.reply_text(
                'Молодой человек, я вас не знаю. Пойдите прочь!'
            )
            return

        if (
            cfg.CONF.mood == 'restrictive'
            and user.responses_today > cfg.CONF.request_limit
        ):
            await update.message.reply_text(
                'Ты задаешь слишком много вопросов. '
                'Лавочка закрывается. Приходи завтра!'
            )
            return

    if user.is_male():
        prefix = 'Дорогой'
    else:
        prefix = 'Милочка'

    if len(prompt) > cfg.CONF.prompt_limit:
        await update.message.reply_text(
            f'{prefix}, ну что-то слишком много букв, '
            f'давай покороче как-нибудь!'
        )
        return

    now = datetime.now()
    if user.last_response is not None:
        delta = (now - user.last_response).total_seconds()
        if delta < cfg.CONF.cooldown:
            await update.message.reply_text(
                f'{prefix}, ну что ты строчишь, '
                f'давай не так быстро, дай мне подумать!'
            )
            return

    data = {
        'model': user.model or cfg.CONF.model,
        'prompt': prompt,
        'stream': False,
    }

    previous_context = await cfg.DB.get_context(user.id)

    if previous_context:
        data['context'] = previous_context

    # делаем вид, что бот печатает, чтобы пользователь был спокойнее
    await context.bot.send_chat_action(
        chat_id=update.message.chat_id,
        action=ChatAction.TYPING,
    )

    try:
        r = httpx.post(
            cfg.CONF.api_url,
            json=data,
            timeout=cfg.CONF.request_timeout,
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

    await cfg.DB.store_response(user, payload)
    await update.message.reply_text(payload['response'])
