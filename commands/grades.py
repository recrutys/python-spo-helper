from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from services.db import *
from services.user import get_user, get_grades

router = Router()

@router.message(Command("grades"))
async def get_grades_command(message: Message):
    tg_user_id = str(message.from_user.id)
    result = get_user(tg_user_id)

    if result['success']:
        user = result['user']

        # Получаем оценки
        grades_result = get_grades(user['session'], user['student_id'])
        if grades_result['success']:
            grades = grades_result['data']
            await message.answer(f"📊 <b>Ваши оценки:</b>\n\n{grades}")
        else:
            await message.answer("❌ Произошла ошибка при получении оценок. Обратитесь к разработчику.")
    else:
        await message.answer("❌ Сначала выполните авторизацию командой /login")