from dotenv import get_key
from telebot import TeleBot
from telebot.types import Message
import logging
from speechkit import Speechkit, users
import db
from icecream import ic


logging.basicConfig(filename='bot.log', encoding='utf-8')
db.init()
bot = TeleBot(get_key('.env', 'TELEGRAM_BOT_TOKEN'))
res = db.get_users()
if res:
    for data in db.get_users():
        Speechkit(data['user_id'], data['chars_remaining'])


@bot.message_handler(commands=['start'])
def send_welcome(message: Message):
    if users:
        if message.from_user.id not in users and len(users) < 3:
            Speechkit(message.from_user.id)
        elif len(users) == 3:
            bot.send_message(message.from_user.id, 'К сожалению, пользователей уже много. Еще и вас мы не потянем)')
            bot.register_next_step_handler_by_chat_id(message.chat.id, looser)
            return
    else:
        Speechkit(message.from_user.id)
    bot.send_message(message.from_user.id, f'Здравствуй, {message.from_user.first_name}! Всего у тебя в запасе'
                                           f' 2000 символов! Чтобы сгенерировать аудиосообщение со своим текстом вам '
                                           f'нужно использовать команду /tts, и ввести текст')


@bot.message_handler(commands=['tts'])
def tts(message: Message):
    bot.send_message(message.from_user.id, 'Отлично! Теперь отправляйте текст')
    bot.register_next_step_handler_by_chat_id(message.chat.id, convert_tts)


def convert_tts(message: Message):
    bot.send_audio(message.from_user.id, users[message.from_user.id].text_to_speech(message.text))


def looser(message: Message):
    bot.send_message(message.from_user.id, 'К сожалению, пользователей уже много. Еще и вас мы не потянем)')
    bot.register_next_step_handler_by_chat_id(message.chat.id, looser)


bot.polling(none_stop=True)
