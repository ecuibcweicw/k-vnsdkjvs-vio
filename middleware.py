from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable

from aiogram.handlers import ErrorHandler
from aiogram.types import Update, TelegramObject
from loguru import logger

from loader import db, bot



class LoggingUsers(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:

        if event.event_type == 'callback_query': #Сравниваем текущий username с юзером из бд, если текущий юзернем не похож с юзером из бд то обновляем его при условии что он есть уже в бд
            logger.info(f"{event.callback_query.from_user.full_name} - {event.callback_query.data}")



        if event.event_type == 'message':
            logger.info(f"{event.message.from_user.full_name} - {event.message.text}")

        return await handler(event, data)