from aiogram import BaseMiddleware
from aiogram.types import Message
from datetime import datetime, timedelta

class RateLimitMiddleware(BaseMiddleware):
    def __init__(self):
        self.user_last_message = {}

    async def __call__(self, handler, event: Message, data):
        user_id = event.from_user.id
        current_time = datetime.now()

        if user_id in self.user_last_message:
            last_time = self.user_last_message[user_id]
            if current_time - last_time < timedelta(seconds=2):
                await event.answer("⏳ Слишком частые запросы! Подождите немного.")
                return  # Полностью прерываем обработку

        self.user_last_message[user_id] = current_time
        return await handler(event, data)