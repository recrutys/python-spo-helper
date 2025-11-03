from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import BufferedInputFile
import os
from services.db import *
from services.user import get_user

router = Router()

@router.message(Command("start"))
async def start_command(message: Message):
    tg_user_id = str(message.from_user.id)
    result = get_user(tg_user_id)

    db = load_db()
    is_new_user = tg_user_id not in db  # Новый пользователь если его нет в базе

    if result['success']:
        user = result['user']
        full_name = user.get('full_name', '')
        group_name = user.get('group_name', '')

        welcome_text = f"🎓 <b>Привет, {full_name} из {group_name}</b>\n"
        welcome_text += "Используйте команду /help для получения подробной информации"
    else:
        welcome_text = "🎓 Здесь вы можете получать свои оценки и следить за успеваемостью.\n\n"
        welcome_text += "Для начала работы необходимо авторизоваться с помощью команды /login"

    # Пытаемся отправить картинку
    tasks_filename = "tasks.jpg"

    if os.path.exists(tasks_filename):
        with open(tasks_filename, 'rb') as photo:
            msg = await message.answer_photo(
                BufferedInputFile(photo.read(), filename=tasks_filename),
                caption=welcome_text
            )
    else:
        msg = await message.answer(welcome_text)

    # Закрепляем сообщение ТОЛЬКО для новых пользователей
    if is_new_user:
        try:
            await message.bot.pin_chat_message(message.chat.id, msg.message_id)
        except Exception as e:
            print(f"ERROR: Не удалось закрепить сообщение: {e}")