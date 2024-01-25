import logging, asyncio, aiocron, html, aiogram
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, types, executor, Dispatcher
from keywords import *
from config import *

from mooh_send import navigate_texts
from mooh_send import announcements
from sub_check import check_user_subs
from new_chat_users import new_chat_users, lv_chat_users

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot)

dp.register_callback_query_handler(navigate_texts, text_contains="btn")

logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename='bot.log', level=logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('bot.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logging.getLogger().addHandler(file_handler)


def create_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Магазин")
    btn2 = types.KeyboardButton("Отзывы")
    btn3 = types.KeyboardButton("Купить")
    markup.add(btn1, btn2, btn3)
    return markup


@dp.message_handler(commands='moohmsg')
async def moo_h_mor(message: types.Message):
    await announcements(message)


@dp.message_handler(commands=['sendbtnchat'])
async def start(message):
    await bot.send_message(chat_id=CHAT_ID, text=BTN_TEXT, parse_mode='Markdown', reply_markup=create_keyboard())


previous_message_id = None


@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def handle_message(message: types.Message):
    global previous_message_id

    await check_user_subs(message)

    text = message.text.lower()

    if len(text.split()) == 1:
        for keyword in LINKS.keys():
            if keyword in text:
                try:
                    if previous_message_id:
                        await bot.delete_message(chat_id=message.chat.id, message_id=previous_message_id)
                except Exception as e:
                    logging.exception(f'Сообщение об обработке ошибок: {message}\n{e}')

                markup = create_keyboard()
                link = LINKS[keyword]
                sent_message = await bot.send_message(chat_id=message.chat.id, text=link, reply_markup=markup)
                previous_message_id = sent_message.message_id
                break

    try:
        if any(keyword in text for keyword in KEYWORDS_ZAKAZ):
            if len(text.split()) == 1:
                keyboard = types.InlineKeyboardMarkup()
                button_zakaz = types.InlineKeyboardButton('Оформить заказ', url='https://t.me/KRAFT_STORE_BOT')
                keyboard.add(button_zakaz)

                sent_message = await bot.send_message(message.chat.id, TEXT_ZAKAZ, parse_mode='Markdown',
                                                      reply_markup=keyboard)
                await asyncio.sleep(TIMER_ERASE)
                await bot.delete_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)

        elif any(keyword in text for keyword in KEYWORDS_BOT):
            if len(text.split()) == 1:
                sent_message = await bot.send_message(message.chat.id, STRORE_BOT, parse_mode='Markdown')

                await asyncio.sleep(TIMER_ERASE)
                await bot.delete_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)

        elif any(keyword in text for keyword in KEYWORDS_TRACK):
            if len(text.split()) == 1:
                sent_message = await bot.send_message(message.chat.id, TRACK_BOT, parse_mode='Markdown')

                await asyncio.sleep(TIMER_ERASE)
                await bot.delete_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)

        elif any(keyword in text for keyword in KEYWORDS_PRICE):
            if len(text.split()) == 1:
                keyboard = types.InlineKeyboardMarkup()
                button_price = types.InlineKeyboardButton('Актуальный прайс', url='https://t.me/krafturpharmacyinfo/96')
                keyboard.add(button_price)

                sent_message = await bot.send_message(message.chat.id, PRICE_TEXT, parse_mode='Markdown',
                                                      reply_markup=keyboard)
                await asyncio.sleep(TIMER_ERASE)
                await bot.delete_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)

    except Exception as e:
        logging.exception(f'Сообщение об обработке ошибок: {message}\n{e}')
        await bot.send_message(message.chat.id, ERROR_TEXT)


async def send_message(chat_id, text):
    formatted_text = html.escape(text)
    try:
        if hasattr(send_message, 'last_message_id'):
            await bot.delete_message(chat_id=chat_id, message_id=send_message.last_message_id)
    except aiogram.utils.exceptions.MessageToDeleteNotFound:
        await bot.send_message(chat_id, ERROR_TEXT)

        pass

    try:
        message = await bot.send_message(chat_id=chat_id, text=formatted_text, parse_mode='Markdown')
        send_message.last_message_id = message.message_id
    except aiogram.utils.exceptions.TelegramAPIError as e:
        logging.exception(f'Сообщение об обработке ошибок: {message}\n{e}')


async def scheduled_task():
    await send_message(CHAT_ID, INFORM_TEXT)


aiocron.crontab(f'{TIMER_INFO} * * * *')(scheduled_task)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    executor.start_polling(dp, skip_updates=True)
    loop.run_forever()
