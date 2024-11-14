import logging

from aiogram import Bot, Dispatcher, executor, types

from config import TOKEN, OWNER_ID
from functions import generate_owner_message_text, generate_owner_caption_text
from models import BannedUsers, session

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    """
    Greeting message for users and for
    the owner!

    :param message:
    :return:
    """
    if message.from_user.id != OWNER_ID:
        return await message.answer("Welcome to the support bot! You can post questions/suggestions here.")
    else:
        return await message.answer("Welcome boss. Enjoy using the bot!")


@dp.message_handler(commands=['mute'])
async def handle_owner_mute_command(message: types.Message):
    """
    This feature mutes these users by
    blacklisting a database that the bot
    owner will flag.

    :param message:
    :return:
    """
    if message.from_user.id == OWNER_ID:
        # get replied message
        replied_message = message.reply_to_message.text

        # get chat id
        chat_id = int(replied_message[replied_message.index('[') + 1:replied_message.index(']')])

        # get name of user
        name_of_user = replied_message.split()[4]

        # check user
        banned_user = session.query(BannedUsers).filter(BannedUsers.telegram_id == chat_id).count()
        if not banned_user:
            chat_id = BannedUsers(telegram_id=chat_id)
            session.add(chat_id)
            session.commit()
            return await message.answer(f"{name_of_user} has been blacklisted")
        return await message.answer(f"{name_of_user} has already been banned")
    return await message.answer('You have no right to this!')


@dp.message_handler(commands=['unmute'])
async def handle_owner_unmute_command(message: types.Message):
    """
    This function unmutes these users by
    removing the users from the blacklisted
    database that the bot owner will mark.

    :param message:
    :return:
    """
    if message.from_user.id == OWNER_ID:
        # get replied message
        replied_message = message.reply_to_message.text

        # get id who sent replied message
        chat_id = int(replied_message[replied_message.index('[') + 1:replied_message.index(']')])

        # get name of user
        name_of_user = replied_message.split()[4]

        # check user id
        chat_id = session.query(BannedUsers).filter(BannedUsers.telegram_id == chat_id)
        if chat_id.count():
            # if user id in black list
            chat_id.delete()
            session.commit()
            return await message.answer(f"{name_of_user} removed from blacklist")
        # if user id is not in black list
        return await message.answer(f'{name_of_user} is not in blacklist')
    return await message.answer("You have no right to this!")


async def handle_owner_message(owner_message: types.Message):
    if not owner_message.reply_to_message:
        return await owner_message.answer("Your message must be a reply to a forwarded message!")

    str_with_customer_chat_id = owner_message.reply_to_message.text if owner_message.reply_to_message.text else owner_message.reply_to_message.caption

    customer_chat_id = 0
    try:
        customer_chat_id = str_with_customer_chat_id[str_with_customer_chat_id.index('[') + 1:str_with_customer_chat_id.index(']')]
    except:
        return await owner_message.answer("You can only reply to forwarded messages!")

    if owner_message.photo:
        return await bot.send_photo(customer_chat_id, owner_message.photo[-1].file_id, caption=owner_message.caption)
    elif owner_message.document:
        return await bot.send_document(customer_chat_id, owner_message.document.file_id, caption=owner_message.caption)
    else:
        return await bot.send_message(customer_chat_id, owner_message.text)

async def handle_customer_message(customer_message: types.Message):
    customer_chat_id = customer_message.from_user.id

    is_blacklisted = session.query(BannedUsers).filter(BannedUsers.telegram_id == customer_chat_id).count() > 0
    if is_blacklisted:
        return await customer_message.answer("You are blacklisted by this bot")

    if customer_message.photo:
        return await bot.send_photo(OWNER_ID, customer_message.photo[-1].file_id, caption=generate_owner_caption_text(customer_message))
    elif customer_message.document:
        return await bot.send_document(OWNER_ID, customer_message.document.file_id, caption=generate_owner_caption_text(customer_message))
    else:
        return await bot.send_message(OWNER_ID, generate_owner_message_text(customer_message))


@dp.message_handler(content_types=types.ContentType.ANY)
async def handle_message(message: types.Message):
    if message.from_user.id == OWNER_ID:
        return await handle_owner_message(message)

    return await handle_customer_message(message)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
