import base64
import json
import random
import time
import traceback
from datetime import datetime
from io import StringIO
from threading import Thread
from typing import List

import schedule
import telebot
from flask import Flask, request
from groq import Groq, BaseModel
from telebot import apihelper
from telebot.types import InputPollOption

from config import *

neuro = Groq(api_key=GROQ_KEY)


class ExHandler(telebot.ExceptionHandler):
    def handle(self, exc):
        sio = StringIO(traceback.format_exc())
        sio.name = 'log.txt'
        sio.seek(0)
        bot.send_document(ME_CHATID, sio)
        return True


bot = telebot.TeleBot(BOT_TOKEN, threaded=True, num_threads=10, parse_mode='HTML', exception_handler=ExHandler())
apihelper.RETRY_ON_ERROR = True
app = Flask(__name__)
bot.remove_webhook()
bot.set_webhook(url=f'{APP_URL}/{BOT_TOKEN}')


@bot.message_handler(commands=["start"])
def msg_start(message):
    bot.reply_to(message, "Скинь мне фото и оно станет новостью")


@bot.message_handler(commands=["generate"])
def msg_generate(message):
    if message.from_user.id == ME_CHATID:
        job_post_news(message.chat.id)


@bot.message_handler(func=lambda message: True, content_types=['photo'])
def msg_photo(message):
    try:
        if message.from_user.id == ME_CHATID:
            post_image(message.photo[-1].file_id, ME_CHATID)
        else:
            post_image(message.photo[-1].file_id)
    except Exception as e:
        bot.reply_to(message, str(e))


def cur_date():
    return datetime.fromtimestamp(time.time() + TIMESTAMP)


def news_text(new, new_tag):
    return f"⚡️<b>{new.title}</b>\n\n{new.text}\n\n#{new_tag.replace(' ', '_').replace('-', '_')}"


class NewModel(BaseModel):
    title: str
    text: str


class PollModel(BaseModel):
    question: str
    options: List[str]


def post_image(file_id, channel=CHANNEL_CHATID):
    # пост с изображением в канал
    new = generate_new_from_img(file_id)
    bot.send_photo(channel, file_id, caption=news_text(new, 'предложка'))
    poll = generate_poll(new.title)
    bot.send_poll(
        channel,
        poll.question,
        [InputPollOption(poll.options[0][:100]), InputPollOption(poll.options[1][:100])],
        True
    )


def job_post_news(channel=CHANNEL_CHATID):
    # пост в канал
    new, new_tag = generate_new()
    bot.send_message(channel, news_text(new, new_tag))
    poll = generate_poll(new.title)
    bot.send_poll(
        channel,
        poll.question,
        [InputPollOption(poll.options[0][:100]), InputPollOption(poll.options[1][:100])],
        True
    )


def generate_poll(title):
    chat_completion = neuro.chat.completions.create(
        messages=[
            {"role": "system",
             "content": LORE},
            {"role": "user",
             "content": f'Составь опрос к новости с таким заголовком: {title}. Опрос должен содержать ровно два \
варианта ответа. Цель опроса это узнать мнение подписчиков канала касательно определённой темы. Опрос должен быть \
провокационным чтобы в нём проголосовало как можно больше людей. Твой ответ должен быть в формате JSON с такими \
полями: вопрос опроса, список из двух вариантов ответа. JSON должен соответствовать этой \
схеме: {json.dumps(PollModel.model_json_schema(), indent=2)}'}
        ],
        response_format={"type": "json_object"},
        model="meta-llama/llama-4-maverick-17b-128e-instruct",
        temperature=TEMPERATURE
    )
    return PollModel.model_validate_json(chat_completion.choices[0].message.content)


def generate_new_from_img(file_id):
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    base64_image = base64.b64encode(downloaded_file).decode('utf-8')
    chat_completion = neuro.chat.completions.create(
        messages=[
            {"role": "system",
             "content": LORE},
            {"role": "user",
             "content": [
                 {
                     "type": "text",
                     "text": f'Напиши новость к которой идеально подойдёт это изображение. Учти что сегодня \
{cur_date().strftime("%d.%m.%Y")}, но не добавляй эту дату в текст. Твой ответ должен быть в формате JSON с такими \
полями: заголовок новости, текст новости. JSON должен соответствовать этой схеме: \
{json.dumps(NewModel.model_json_schema(), indent=2)}'
                 },
                 {
                     "type": "image_url",
                     "image_url": {
                         "url": f"data:image/jpeg;base64,{base64_image}"
                     }
                 }
             ]}
        ],
        response_format={"type": "json_object"},
        model="meta-llama/llama-4-maverick-17b-128e-instruct",
        temperature=TEMPERATURE
    )
    return NewModel.model_validate_json(chat_completion.choices[0].message.content)


def generate_new():
    new_tag = random.choice(NEW_TAGS)
    chat_completion = neuro.chat.completions.create(
        messages=[
            {"role": "system",
             "content": LORE},
            {"role": "user",
             "content": f'Напиши новость на тему "{new_tag}". Учти что сегодня {cur_date().strftime("%d.%m.%Y")}, \
но не добавляй эту дату в текст. Твой ответ должен быть в формате JSON с такими полями: заголовок новости, текст \
новости. JSON должен соответствовать этой схеме: {json.dumps(NewModel.model_json_schema(), indent=2)}'}
        ],
        response_format={"type": "json_object"},
        model="meta-llama/llama-4-maverick-17b-128e-instruct",
        temperature=TEMPERATURE
    )
    return NewModel.model_validate_json(chat_completion.choices[0].message.content), new_tag


@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return 'ok', 200


@app.route('/')
def get_ok():
    return 'ok', 200


def updater():
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    schedule.every(12).hours.do(job_post_news)
    Thread(target=updater).start()
    bot.send_message(ME_CHATID, 'Запущено')
    app.run(host='0.0.0.0', port=80, threaded=True)
