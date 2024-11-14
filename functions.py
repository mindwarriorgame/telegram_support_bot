from aiogram.types import Message

def generate_owner_text(customer_message: Message, text_or_caption: str):
    if customer_message.from_user.username is not None:
        edited_message = f"Message from user [{customer_message.from_user.id}] {customer_message.from_user.username}: " \
                         f"\n \n {text_or_caption}"
    else:
        edited_message = f"Message from user [{customer_message.from_user.id}] {customer_message.from_user.full_name}: " \
                         f"\n \n {text_or_caption}"
    return edited_message


def generate_owner_message_text(customer_message: Message):
    return generate_owner_text(customer_message, customer_message.text)

def generate_owner_caption_text(customer_message: Message):
    return generate_owner_text(customer_message, customer_message.caption)
