from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import BufferedInputFile
import os
from services.db import *
from services.user import get_user

router = Router()

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from services.db import load_config

router = Router()

@router.message(Command("help"))
async def command_help(message: Message):
    tg_user_id = str(message.from_user.id)
    config = load_config()
    is_admin = tg_user_id in config.get("admin_ids", [])

    # Базовые команды для всех
    user_commands = [
        "🔐 <b>/login</b> - Авторизация в системе",
        "📊 <b>/grades</b> - Получить текущие оценки",
        "🆔 <b>/my_id</b> - Узнать свой Telegram ID",
        "🆘 <b>/help</b> - Показать эту справку"
    ]

    # Команды только для админов
    admin_commands = [
        "📢 <b>/broadcast</b> - Сделать рассылку всем пользователям",
        "📢 <b>/unpin_all</b> - Открепить всё, что закреплено у пользователей",
        "👤 <b>/add_admin</b> - Добавить администратора",
        "👤 <b>/remove_admin</b> - Удалить администратора",
        "👤 <b>/users_list</b> - Логины пользователей в боте"
    ]

    # Форматирование оценок
    grade_legend = [
        "📝 <b>Формат оценок:</b>",
        "5/4/3/2 - Оценки",
        "🟡 ув - Уважительная причина",
        "🔴 нп - Неуважительная причина",
        "🏥 бл - Больничный"
    ]

    # Собираем финальный текст
    help_text = "🤖 <b>Доступные команды:</b>\n\n"

    # Команды пользователя
    help_text += "\n".join(user_commands)

    # Команды админа (если есть права)
    if is_admin:
        help_text += "\n\n👨‍💼 <i>Админ-команды:</i>\n"
        help_text += "\n".join(admin_commands)

    # Легенда оценок
    help_text += "\n\n" + "\n".join(grade_legend)

    await message.answer(help_text)