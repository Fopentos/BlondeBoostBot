import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import init_db
from handlers import router as user_router
from admin import router as admin_router
from handlers import load_services, status_checker

async def main():
    logging.basicConfig(level=logging.INFO)
    init_db()
    await load_services()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(user_router)
    dp.include_router(admin_router)
    asyncio.create_task(status_checker())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())