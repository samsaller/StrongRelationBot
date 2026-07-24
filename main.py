import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
import database as db
from handlers import start, pairing, messages, discussion

logging.basicConfig(level=logging.INFO)

async def main():
    # Инициализация БД
    await db.init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Подключение роутеров
    dp.include_router(start.router)
    dp.include_router(pairing.router)
    dp.include_router(discussion.router)
    dp.include_router(messages.router)

    logging.info("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())