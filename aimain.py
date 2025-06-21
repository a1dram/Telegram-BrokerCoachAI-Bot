import asyncio
import os


from aiogram import Router, Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode


from data.database import init_models
from routers.init import router

from config import bot

async def main():
    await init_models()

    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot, skip_updates=False)

if __name__ == '__main__':
    os.environ['DEBUG'] = 'True'
    asyncio.run(main())
