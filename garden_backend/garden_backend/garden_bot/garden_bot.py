import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garden_backend.garden_backend.settings')
django.setup()

import telebot
from garden_backend.garden_backend.settings import BOT_TOKEN
from telebot import types
from garden_backend.garden_backend.garden_bot.user_functions import is_register, register, find_user
from garden_backend.garden_backend.garden_bot.garden_functions import gardens_meters


bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(content_types=["text"])
def any_msg(message):
    keyboardmain = types.InlineKeyboardMarkup(row_width=2)
    registration_button = types.InlineKeyboardButton(text="Зарегистрироваться", callback_data="registration")
    meters_button = types.InlineKeyboardButton(text="Ввести показания", callback_data="meters")
    keyboardmain.add(registration_button, meters_button)
    bot.send_message(message.chat.id, 'Добрый день! Выберите действие', reply_markup=keyboardmain)


@bot.callback_query_handler(func=lambda call: call.data == 'registration')
def phone(call):
    keyboard = types.ReplyKeyboardMarkup(row_width=1)
    button_phone = types.KeyboardButton(text="Отправить телефон", request_contact=True)
    keyboard.add(button_phone)
    bot.send_message(call.message.chat.id,
                     'Пожалуйста, отправьте свой номер через кнопку ниже'
                     '\n\n Если вы уже зарегистрированы, то отправлять контакт не нужно. '
                     '\n\n Для возврата в основное меню введите любой текст',
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'meters')
def phone(call):
    msg = bot.send_message(call.message.chat.id, 'Пожалуйста введите свой логин')
    bot.register_next_step_handler(msg, check_login_to_meters)


@bot.message_handler(content_types=['contact'])
def contact(message):
    print(message)
    if message.contact is not None:
        phone = message.contact.phone_number
        chat_id = message.chat.id
        try:
            registered_phone = is_register(phone)
            if not registered_phone:
                result = register(phone, chat_id)
                login = result['login']
                password = result['password']
                bot.send_message(message.chat.id,
                                 f'Ваш логин - {login}, пароль - {password}.\n\n Пожалуйста, запомните или запишите их, они будут использоваться для передачи показаний')
            else:
                bot.send_message(message.chat.id,
                                 'Такой номер уже зарегистрирован, если Вы забыли пароль - обратитесь к администратору')
        except Exception:
            bot.send_message(message.chat.id,
                             'Попробуйте ещё раз отправить номер телефона или обратитесь к администратору')


def check_login_to_meters(message):
    login = message.text
    user = find_user(username=message.text)
    if user:
        msg = bot.send_message(message.chat.id, 'Пожалуйста введите пароль')
        bot.register_next_step_handler(msg, check_password_to_meters, login)
    else:
        bot.send_message(message.chat.id, 'Такой логин не найден, пожалуйста начните сначала вводом любого текста')


def check_password_to_meters(message, login):
    user = find_user(username=login)
    if user.check_password(raw_password=message.text):
        msg = bot.send_message(message.chat.id, 'Пожалуйста введите показания')
        bot.register_next_step_handler(msg, enter_meters, login)
    else:
        bot.send_message(message.chat.id,
                         'Введена некорректная пара логин/пароль. Для того, чтобы попробовать снова введите любой текст')

# доделать
def enter_meters(message, login):
    meters = gardens_meters(login)
    info = ""
    for garden_plot, last_meters in meters.items():
        info += f'Участок - {garden_plot}, предыдущие показания {last_meters[0]}, были получены {last_meters[1]}\n\n'

    msg = bot.send_message(message.chat.id,
                     info)



def send_notification(chat_id, text):
    bot.send_message(chat_id, text)


bot.polling(none_stop=True)
