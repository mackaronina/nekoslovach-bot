from aiogram.types import Message


def escape_brackets(text: str) -> str:
    return text.replace('{', '{{').replace('}', '}}')


def post_to_text(message: Message) -> str:
    if message.poll is not None:
        return f'Опрос. {message.poll.question}\n1. {message.poll.options[0].text}\n2. {message.poll.options[1].text}'
    return message.text or message.caption
