from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import BufferedInputFile
from services.db import *
import os
import asyncio

router = Router()

@router.message(Command("users_list"))
async def command_users_list(message: Message):
    user_id = str(message.from_user.id)
    config = load_config()
    ADMIN_IDS = config.get("admin_ids", [])

    if user_id not in ADMIN_IDS:
        await message.answer("❌ У вас нет прав")
        return

    db = load_db()

    if not db:
        await message.answer("📋 База пользователей пуста")
        return

    users_text = "📋 <b>Пользователи в боте:</b>\n\n"

    for i, (tg_id, user_data) in enumerate(db.items(), 1):
        login = user_data.get('login', 'N/A')

        if tg_id in ADMIN_IDS:
            users_text += f"{i}. <code>{login}</code>* (ID: <code>{tg_id}</code>)\n"
        else:
            users_text += f"{i}. <code>{login}</code> (ID: <code>{tg_id}</code>)\n"

    users_text += "\n* - администратор"

    await message.answer(users_text)