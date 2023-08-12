from aiogram import types, Bot
from config import *
import logging

bot = Bot(token=TOKEN)


def create_inline_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn_subs = types.InlineKeyboardButton("Подписаться", url="https://t.me/krafturpharmacyinfo")

    markup.add(btn_subs)
    return markup


async def check_subscription(chat_id, channel_username):
    try:
        chat_member = await bot.get_chat_member(channel_username, chat_id)
        if chat_member.status in (
                types.ChatMemberStatus.MEMBER, types.ChatMemberStatus.ADMINISTRATOR, types.ChatMemberStatus.CREATOR):
            return True
        else:
            return False
    except Exception as e:
        logging.error(str(e))
        return False


async def check_user_subs(message: types.Message):
    user_id = message.from_user.id
    channel_username = '@krafturpharmacyinfo'
    is_subscribed = await check_subscription(user_id, channel_username)
    if is_subscribed is False:
        await message.reply("Пожалуйста, подпишитесь на канал, чтобы не пропускать важные новости!👍",
                            reply_markup=create_inline_keyboard())
