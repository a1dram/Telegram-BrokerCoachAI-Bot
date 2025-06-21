from random import choice, randint

from sqlalchemy import select

from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram import Router
from aiogram.fsm.context import FSMContext

from data import database
from data.user_form import User

from utils.forms import Form
from utils.keyboards import end_dialog_kb, start_dialog_kb, start_registration_kb
from utils.ai_plugins import get_ai_answer, get_the_dialog_analysis
from utils.help_ai_info import traits, person
from utils.help_functions import get_structured_dialog

from config import bot

broker_router = Router(name=__name__)


@broker_router.message(Command("start"))
@broker_router.message(Form.new_dialog)
async def answer(message: Message, state: FSMContext):
    s_user_id = str(message.from_user.id)
    username = message.from_user.username

    sess = await database.create_session()
    user = await sess.execute(select(User).filter_by(
        user_id=s_user_id
    ))

    user = user.scalars().first()
    if not user:
        user = User(
            user_id=s_user_id,
            username=username,
        )
        sess.add(user)
    else:
        user.username = username

    phone_number = user.phone_number

    user.dialog_have = False
    user.dialog = ""

    await sess.commit()
    await sess.close()
    reg_caption = (f"<b>👋 Привет! Добро пожаловать в нашего бота для обучения брокеров по "
                   f"недвижимости.</b>\n\n"
                   "<b>•</b> Освоить холодные звонки.\n"
                   "<b>•</b> Улучшить навыки работы с возражениями.\n"
                   "<b>•</b> Увеличить конверсию и уверенность в переговорах.\n\n"
                   f"Для начала создадим ваш профиль, чтобы сохранить прогресс вашего обучения.")
    main_caption = (f"<b>👋 Приветствуем вас, {username}</b>\n\n"
                    f"Вы находитесь на главном меню бота,\n"
                    f"выберите действие: ")
    await bot.send_photo(chat_id=s_user_id, photo=FSInputFile("./static/hello_image.PNG"),
                         caption=main_caption if phone_number else reg_caption,
                         reply_markup=start_dialog_kb() if phone_number else start_registration_kb())
    if phone_number:
        await state.set_state(Form.msg)
    else:
        await state.set_state(Form.register)


@broker_router.message(Form.register)
async def register(message: Message, state: FSMContext):
    phone = str(message.contact.phone_number)
    sess = await database.create_session()
    user = await sess.execute(select(User).filter_by(
        user_id=str(message.from_user.id))
    )
    user = user.scalars().first()
    user.phone_number = phone
    await sess.commit()
    await sess.close()
    await answer(message, state)


@broker_router.message(Form.msg)
@broker_router.message(F.text == 'Начать холодный звонок')
async def start_a_dialog(message: Message, state: FSMContext):
    try:
        s_user_id = str(message.from_user.id)
        await state.clear()
    except Exception as err:
        await message.answer("Сообщение не является текстовым")
        return

    sess = await database.create_session()
    user = await sess.execute(select(User).filter_by(user_id=s_user_id))
    user = user.scalars().first()

    if not user.phone_number:
        await message.answer("Перед использованием функций бота нам нужно убедиться в достоверности вашего аккаунта.\n")

    # Хеппи Енд нужен для учитывания различных концовок (в основном редких)
    async def end_a_dialog(dialog: str):
        user.dialog_have = False

        if dialog.count(';;'):
            dialog: str = get_structured_dialog(old_dialog=dialog, request_type='analysis')

            # Функция, которая собирает и анализирует всю инфу с user.dialog
            dialog_analysis = get_the_dialog_analysis(dialog=dialog)

            await message.answer(f"✨ <b>Спасибо за звонок!</b>\n\n"
                                 f"{dialog_analysis}\n\n"
                                 "<b>Провести еще один звонок?</b>",
                                 reply_markup=start_dialog_kb())

        else:
            await message.answer("<b>Спасибо за звонок!</b>", reply_markup=start_dialog_kb())

    if message.text == 'Завершить звонок':
        await end_a_dialog(dialog=user.dialog + '\n\n' + 'Брокер завершил звонок.')
        user.dialog = ""
        await sess.commit()

    elif message.text == 'Начать холодный звонок':
        if user.dialog:
            user.dialog = ""

        user.client_personality = str(choice(person))
        user.client_trait = str(choice(traits))
        user.dialog_have = True

        await sess.commit()
        await message.answer('Звонок начался.', reply_markup=end_dialog_kb())

    else:
        if not user.dialog_have:
            await message.answer('<b>Чтобы начать холодный звонок, нажмите на кнопку ниже.</b>')

        else:
            user.dialog += f';;{message.text}' if user.dialog else message.text

            # Специальный переделанный диалог для работы с ним нейросети
            live_dialog = get_structured_dialog(old_dialog=user.dialog)

            ai_answer: str = get_ai_answer(message=message.text, live_dialog=live_dialog, user=user)

            if ai_answer:
                user.dialog += f';;{ai_answer}'

                if '*УСПЕХ' in ai_answer:
                    ai_answer = ai_answer.replace('*УСПЕХ', '')

                    for i in '*_-`':
                        if i in ai_answer:
                            ai_answer = ai_answer.replace(i, '')

                    if not ai_answer or len(ai_answer) < 3:
                        good_end = [
                            'Отлично, до встречи!', 'Хорошо, до свидания!', 'До встречи! Хорошего дня.',
                            'Большое спасибо, до скорых встреч!', 'До свидания!', 'Спасибо, до свидания.'
                        ]
                        ai_answer = choice(good_end)

                    await message.answer(ai_answer)

                    happy_end = '<b>🤩 Клиент готов встретиться, отличная работа!</b>'

                    await message.answer(happy_end)
                    await end_a_dialog(dialog=user.dialog + happy_end)
                    user.dialog = ""

                else:
                    bye_reason = ''

                    if '*GOODBYE' in ai_answer:
                        bye_reason = '*GOODBYE'

                    if '*BLACKLIST' in ai_answer:
                        bye_reason = '*BLACKLIST'

                    ai_answer = ai_answer.replace(bye_reason, '').replace('*', '')

                    if ai_answer:
                        await message.answer(ai_answer)

                    if bye_reason == '*GOODBYE':
                        await end_a_dialog(dialog=user.dialog)
                        user.dialog = ""

                    if bye_reason == '*BLACKLIST':
                        happy_end = '<b>🚫 Клиент отправил вас в чёрный список.</b>'
                        await message.answer(happy_end)
                        await end_a_dialog(dialog=user.dialog + '\n\n🚫 Клиент отправил брокера в чёрный список')
                        user.dialog = ""

                    # ban_phrases = ['чёрный список', 'прекращаю наш разговор', 'прекращу наш разговор',
                    #                'не тратьте мое время', 'смысла в продолжении', 'я не могу продолжать общение',
                    #                'другому брокеру', 'другого брокера', 'продолжать разговор с вами',
                    #                'я не собираюсь продолжать', 'удалил из контактов.']
                    #
                    # bye_phrases = ['до свидания', 'хорошего дня', 'всего доброго', 'до связи',
                    #                'до встречи', 'до скорых встреч']

                    # for check in ban_phrases:
                    #     if check in ai_answer.lower():
                    #         happy_end = '<b>🚫 Клиент отправил вас в чёрный список.</b>'
                    #
                    #         await message.answer(happy_end)
                    #         await end_a_dialog(dialog=user.dialog + '\n\n🚫 Клиент отправил брокера в чёрный список')
                    #         user.dialog = ""
                    #
                    # for check in bye_phrases:
                    #     if check in ai_answer.lower():
                    #         await end_a_dialog(dialog=user.dialog)
                    #         user.dialog = ""

                await sess.commit()
            else:
                msg = '<b>😰 У клиента отключился интернет. Упс...</b>'

                await message.answer(msg)
                await end_a_dialog(dialog=user.dialog + '\n\n' + msg)
                user.dialog = ""
                await sess.commit()

    await sess.close()
    await state.set_state(Form.msg)
