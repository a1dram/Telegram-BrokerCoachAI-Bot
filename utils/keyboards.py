from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def start_registration_kb():
    button = KeyboardButton(text='Создать профиль', request_contact=True)
    kb = ReplyKeyboardMarkup(keyboard=[[button]], resize_keyboard=True, one_time_keyboard=True)
    return kb


def start_dialog_kb():
    button = KeyboardButton(text='Начать холодный звонок')
    kb = ReplyKeyboardMarkup(keyboard=[[button]], resize_keyboard=True, one_time_keyboard=True)
    return kb


def end_dialog_kb():
    button = KeyboardButton(text='Завершить звонок')
    kb = ReplyKeyboardMarkup(keyboard=[[button]], resize_keyboard=True, one_time_keyboard=True)
    return kb
