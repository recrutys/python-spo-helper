from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from services.db import *
from services.user import auth
import asyncio

router = Router()

@router.message(Command("login"))
async def login_command(message: Message):
    tg_user_id = str(message.from_user.id)

    # Проверяем, не авторизован ли уже пользователь
    db = load_db()
    if tg_user_id in db:
        user = db[tg_user_id]
        await message.answer(
            f"🔐 <b>Вы уже авторизованы!</b>\n\n"
            f"👤 <b>Студент:</b> {user.get('full_name', 'Неизвестно')}\n"
            f"👥 <b>Группа:</b> {user.get('group_name', 'Неизвестно')}\n\n"
            f"Если хотите войти под другим аккаунтом, просто отправьте логин:пароль"
        )
        return

    # Отправляем сообщение и удаляем через 30 секунд
    msg = await message.answer(
        "🔐 <b>Авторизация</b>\n\n"
        "Для входа в систему отправьте ваш логин и пароль в формате:\n"
        "<code>логин:пароль</code>\n\n"
        "⚠️ <i>Сообщение будет автоматически удалено через 30 секунд</i>"
    )

    # Удаляем через 30 секунд
    await asyncio.sleep(30)
    try:
        await msg.delete()
    except:
        pass  # Если сообщение уже удалено

@router.message(F.text.contains(':'))
async def process_login(message: Message):
    tg_user_id = str(message.from_user.id)

    try:
        login, password = message.text.split(':', 1)
        login = login.strip()
        password = password.strip()

        if not login or not password:
            await message.answer("❌ Неверный формат. Используйте: логин:пароль")
            return

        # Удаляем сообщение с паролем для безопасности
        await message.delete()

        # Авторизация
        result = auth(login, password) # вызов из модуля services/user.py

        if result['success']:
            # Сохраняем данные пользователя
            db = load_db()
            db[tg_user_id] = {  # исправлено: было user_id, должно быть tg_user_id
                'login': login,
                'password': password,
                'session': result['session'].get_dict() if 'session' in result else None,
                'student_id': result.get('student_id'),
                'full_name': result.get('full_name', ''),
                'group_name': result.get('group_name', '')
            }
            save_db(db)

            welcome_text = f"✅ <b>Авторизация успешна!</b>\n\n"
            if result.get('full_name'):
                welcome_text += f"👤 <b>Студент:</b> {result['full_name']}\n"
            if result.get('group_name'):
                welcome_text += f"👥 <b>Группа:</b> {result['group_name']}\n"
            welcome_text += f"\nТеперь вы можете получить свои оценки с помощью команды /grades"

            await message.answer(welcome_text)
        else:
            await message.answer(f"❌ <b>Ошибка авторизации:</b>\n{result['error']}")

    except ValueError:
        await message.answer("❌ Неверный формат. Используйте: логин:пароль")
    except Exception as e:
        await message.answer("❌ Произошла ошибка при авторизации")