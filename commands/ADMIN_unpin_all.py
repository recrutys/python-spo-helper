from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import BufferedInputFile
from services.db import *
import os
import asyncio

router = Router()

@router.message(Command("unpin_all"))
async def command_unpin_all(message: Message):
    user_id = str(message.from_user.id)
    config = load_config()
    ADMIN_IDS = config.get("admin_ids", [])

    if user_id not in ADMIN_IDS:
        await message.answer("❌ У вас нет прав")
        return

    db = load_db()
    users_count = len(db)
    success_count = 0

    status_msg = await message.answer(f"📢 <b>Открепляю...</b>\nПользователей: {users_count}")

    for user_id in db.keys():
        try:
            await message.bot.unpin_all_chat_messages(int(user_id))
            success_count += 1
        except Exception as e:
            print(f"Ошибка: {e}")

        await asyncio.sleep(0.1)

    await status_msg.edit_text(f"✅ Откреплено: {success_count}/{users_count}")