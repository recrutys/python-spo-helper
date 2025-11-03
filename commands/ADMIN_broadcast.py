from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import BufferedInputFile
from services.db import *
import os
import asyncio

router = Router()

# не понимаю что тут написано, нейросеть спасибо <3
@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message):
    user_id = str(message.from_user.id)
    config = load_config()
    ADMIN_IDS = config.get("admin_ids", [])

    if user_id not in ADMIN_IDS:
        await message.answer("❌ У вас нет прав для использования этой команды")
        return

    # Проверяем есть ли прикрепленное фото
    has_photo = message.photo is not None

    # Получаем текст: из caption если есть фото, иначе из text
    if has_photo:
        # Если есть фото - текст в caption
        full_text = message.caption or ""
    else:
        # Если нет фото - текст в message.text
        full_text = message.text or ""

    # Убираем команду /broadcast и флаги из текста
    parts = full_text.split(' ')
    should_pin = 'pin' in parts

    # Убираем команду и флаги, оставляем только текст сообщения
    clean_parts = [p for p in parts if p not in ['/broadcast', 'broadcast', 'pin']]
    clean_text = ' '.join(clean_parts).strip()

    # Добавляем "ОБЪЯВЛЕНИЕ" только если есть текст
    if clean_text:
        broadcast_text = "❗️ <b>ОБЪЯВЛЕНИЕ</b> ❗️\n\n" + clean_text
    else:
        broadcast_text = "❗️ <b>ОБЪЯВЛЕНИЕ</b> ❗️"

    # Проверяем есть ли хоть что-то для отправки
    if not clean_text and not has_photo:
        await message.answer(
            "<b>Использование:</b>\n"
            "1. Просто текст:\n"
            "<code>/broadcast Ваше сообщение</code>\n\n"
            "2. Текст + фото (прикрепите фото):\n"
            "<code>/broadcast</code> + фото с подписью\n\n"
            "3. С закрепом - добавьте 'pin':\n"
            "<code>/broadcast pin Ваше сообщение</code>\n"
            "Или: <code>/broadcast pin</code> + фото с подписью"
        )
        return

    db = load_db()
    users_count = len(db)
    success_count = 0

    status_msg = await message.answer(f"📢 <b>Начинаю рассылку...</b>\nПолучателей: {users_count}")

    # Если есть фото - скачиваем его
    photo_data = None
    if has_photo:
        photo = message.photo[-1]  # Берем самую качественную версию
        file_info = await message.bot.get_file(photo.file_id)
        downloaded_file = await message.bot.download_file(file_info.file_path)
        photo_data = downloaded_file.read()

    # Рассылка
    for user_id in db.keys():
        try:
            if has_photo and photo_data:
                # Отправляем фото + текст
                msg = await message.bot.send_photo(
                    chat_id=int(user_id),
                    photo=BufferedInputFile(photo_data, filename="broadcast.jpg"),
                    caption=broadcast_text
                )
            else:
                # Отправляем только текст
                msg = await message.bot.send_message(
                    chat_id=int(user_id),
                    text=broadcast_text
                )

            # Закрепляем если нужно
            if should_pin:
                await message.bot.pin_chat_message(int(user_id), msg.message_id)

            success_count += 1

        except Exception as e:
            print(f"Ошибка отправки пользователю {user_id}: {e}")

        await asyncio.sleep(0.1)

    await status_msg.edit_text(
        f"✅ <b>Рассылка завершена!</b>\n\n"
        f"Успешно: {success_count}/{users_count}\n"
        f"Фото: {'✅' if has_photo else '❌'}\n"
        f"Закреп: {'✅' if should_pin else '❌'}"
    )