from aiogram import BaseMiddleware
from aiogram.types import Message, ErrorEvent
from aiogram.exceptions import TelegramAPIError
import requests
from services.db import load_config

class ErrorHandlerMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):
        try:
            return await handler(event, data)

        except requests.exceptions.ConnectionError:
            await event.answer("🔧 <b>Сайт временно недоступен</b>\n\nПопробуйте позже, возможно идут технические работы.")
            return

        except requests.exceptions.Timeout:
            await event.answer("⏰ <b>Превышено время ожидания</b>\n\nСайт перегружен, попробуйте через пару минут.")
            return

        except Exception as e:
            # Игнорируем ошибки от админов (для отладки)
            config = load_config()
            if str(event.from_user.id) not in config.get("admin_ids", []):
                await event.answer("🔧 <b>Временные технические неполадки</b>\n\nПопробуйте позже.")
            else:
                # Админам показываем полную ошибку
                await event.answer(f"🐛 <b>Ошибка для админа:</b>\n<code>{str(e)}</code>")
            return