from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import BufferedInputFile
import os
from services.db import *
from services.user import get_user

router = Router()

@router.message(Command("my_id"))
async def command_my_id(message: Message):
    user_id = str(message.from_user.id)
    await message.answer(f"🆔 <b>Ваш ID:</b> <code>{user_id}</code>")