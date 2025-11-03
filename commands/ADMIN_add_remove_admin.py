from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import BufferedInputFile
import os
from services.db import *
from services.user import get_user

router = Router()

@router.message(Command("add_admin"))
async def command_add_admin(message: Message):
    user_id = str(message.from_user.id)
    config = load_config()
    ADMIN_IDS = config.get("admin_ids", [])

    if user_id not in ADMIN_IDS:
        await message.answer("❌ У вас нет прав")
        return

    # Получаем ID нового админа из команды
    parts = message.text.split(' ')
    if len(parts) < 2:
        await message.answer("❌ Использование: /add_admin user_id")
        return

    new_admin_id = parts[1].strip()

    # Проверяем валидность ID
    if not new_admin_id.isdigit():
        await message.answer("❌ ID должен состоять только из цифр")
        return

    # Проверяем не добавлен ли уже
    if new_admin_id in ADMIN_IDS:
        await message.answer("❌ Этот пользователь уже админ")
        return

    # Добавляем в конфиг
    ADMIN_IDS.append(new_admin_id)
    config['admin_ids'] = ADMIN_IDS
    save_config(config)

    await message.answer(f"✅ Пользователь {new_admin_id} добавлен в админы")

@router.message(Command("remove_admin"))
async def command_remove_admin(message: Message):
    user_id = str(message.from_user.id)
    config = load_config()
    ADMIN_IDS = config.get("admin_ids", [])

    if user_id not in ADMIN_IDS:
        await message.answer("❌ У вас нет прав")
        return

    # Получаем ID админа для удаления
    parts = message.text.split(' ')
    if len(parts) < 2:
        await message.answer("❌ Использование: /remove_admin user_id")
        return

    remove_admin_id = parts[1].strip()

    # Проверяем существует ли
    if remove_admin_id not in ADMIN_IDS:
        await message.answer("❌ Этот пользователь не админ")
        return

    # Не даем удалить себя
    if remove_admin_id == user_id:
        await message.answer("❌ Нельзя удалить себя")
        return

    # Удаляем из конфига
    ADMIN_IDS.remove(remove_admin_id)
    config['admin_ids'] = ADMIN_IDS
    save_config(config)

    await message.answer(f"✅ Пользователь {remove_admin_id} удален из админов")