import os
import logging

from dotenv import load_dotenv, find_dotenv

from groq import Groq

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

load_dotenv(find_dotenv())
logging.basicConfig(level=logging.INFO)

LLAMA_MODEL = 'llama3-70b-8192'

GROQ_TOKEN = os.getenv('GROQ_TOKEN')
GROQ_CLIENT = Groq(api_key=GROQ_TOKEN)

TOKEN = os.getenv('TOKEN')

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
