# -*- coding: utf-8 -*-

import os
import sys
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from services.db import *
from middlewares.rate_limit import RateLimitMiddleware
from middlewares.site_errors import ErrorHandlerMiddleware
from aiogram.types import BotCommand, BotCommandScopeChat

class MyBot:
    def __init__(self):
        self.config = load_config()
        self.db = load_db()

        self.bot = Bot(token=self.config['bot_token'], default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        self.dp = Dispatcher()

        # Регистрируем middleware на спам защиту
        self.dp.message.middleware(RateLimitMiddleware())
        print(f"Спам-защита работает")

        # Регистрируем middleware если сайт ляжет
        self.dp.update.middleware(ErrorHandlerMiddleware())

        # Загружаем все команды
        self._load_commands()

    async def _set_commands(self):
        """Устанавливает список команд в меню бота"""
        commands = [
            BotCommand(command="start", description="Начать работу"),
            BotCommand(command="login", description="Авторизация"),
            BotCommand(command="grades", description="Мои оценки"),
            BotCommand(command="my_id", description="Мой ID"),
            BotCommand(command="help", description="Помощь"),
        ]

        # Команды для админов
        admin_commands = [
            BotCommand(command="broadcast", description="Рассылка (админ)"),
            BotCommand(command="users_list", description="Список пользователей (админ)"),
            BotCommand(command="unpin_all", description="Открепить всё (админ)"),
            BotCommand(command="add_admin", description="Добавить админа (админ)"),
            BotCommand(command="remove_admin", description="Удалить админа (админ)"),
        ]

        # Устанавливаем команды для всех
        await self.bot.set_my_commands(commands)

        # Устанавливаем команды для админов
        config = load_config()
        for admin_id in config.get("admin_ids", []):
            try:
                await self.bot.set_my_commands(
                    commands + admin_commands,
                    scope=BotCommandScopeChat(chat_id=int(admin_id))
                )
            except:
                pass

    def _load_commands(self):
        # Загружает все хендлеры команд
        try:
            import commands

            # Ищем все файлы с командами
            for filename in os.listdir("commands"):
                if filename.endswith(".py"):
                    module_name = f"commands.{filename[:-3]}"
                    module = __import__(module_name, fromlist=[''])

                    # Регистрируем роутер если он есть
                    if hasattr(module, 'router'):
                        self.dp.include_router(module.router)
                        print(f"Загружена команда: {filename}")

        except ImportError as e:
            print(f"Ошибка загрузки команд: {e}")

    def run(self):
        print("Бот запущен!")

        # Запускаем всё в одном event loop
        asyncio.run(self._start_bot())

    async def _start_bot(self):
        await self._set_commands()
        await self.dp.start_polling(self.bot)

bot = MyBot()
bot.run()