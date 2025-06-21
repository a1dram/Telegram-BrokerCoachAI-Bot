from groq import Groq

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

GROQ_TOKEN = "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"
GROQ_CLIENT = Groq(api_key=GROQ_TOKEN)

LLAMA_MODEL = 'llama3-70b-8192'

# broker_mvp_bot
# mvp bot token
token = '7516487658:AAGF6Bh_H1bsRwDfmAMXvCH0aciSZWvMXqY'

# broker_test1_bot
# token = '7893263539:AAGohGQk6KkYc8RTUFMfJzkjOvEgeuO0F-0'

bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
