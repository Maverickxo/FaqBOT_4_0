from aiogram import types, Bot
from config import *
import logging

bot = Bot(token=TOKEN)


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
