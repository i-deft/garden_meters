import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gardens_meters.gardens_meters.settings')
django.setup()

import telebot
from gardens_meters.gardens_meters.settings import BOT_TOKEN
from telebot import types
from gardens_meters.gardens_meters.garden_bot.user_functions import is_register, register, find_user
from gardens_meters.gardens_meters.garden_bot.garden_functions import garden_preivous_meters, garden_is_exist, register_garden, \
    garden_plots, delete_garden

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(content_types=["text"])
def any_msg(message):
    keyboardmain = types.InlineKeyboardMarkup(row_width=2)
    registration_button = types.InlineKeyboardButton(text="Зарегистрироваться", callback_data="registration")
    meters_button = types.InlineKeyboardButton(text="Ввести показания", callback_data="meters")
    keyboardmain.add(registration_button, meters_button)
    bot.send_message(message.chat.id, 'Добрый день! Выберите действие', reply_markup=keyboardmain)


@bot.callback_query_handler(func=lambda call: call.data == 'registration')
def registration(call):
    keyboard = types.ReplyKeyboardMarkup(row_width=1)
    button_phone = types.KeyboardButton(text="Отправить телефон", request_contact=True)
    keyboard.add(button_phone)
    bot.send_message(call.message.chat.id,
                     'Пожалуйста, отправьте свой номер через кнопку ниже'
                     '\n\n Если вы уже зарегистрированы, то отправлять контакт не нужно. '
                     '\n\n Для возврата в основное меню введите любой текст',
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'meters')
def meters(call):
    msg = bot.send_message(call.message.chat.id, 'Пожалуйста введите свой логин')
    bot.register_next_step_handler(msg, check_login_to_meters)


@bot.message_handler(content_types=['contact'])
def contact(message):
    if message.contact is not None:
        phone = message.contact.phone_number
        chat_id = message.chat.id
        try:
            if not is_register(phone):
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
    user = is_register(login=message.text)
    if user:
        msg = bot.send_message(message.chat.id, 'Пожалуйста введите пароль')
        bot.register_next_step_handler(msg, check_password_to_meters, login)
    else:
        bot.send_message(message.chat.id, 'Такой логин не найден, пожалуйста начните сначала вводом любого текста')


def check_password_to_meters(message, login):
    user = find_user(login=login)
    if user.check_password(raw_password=message.text):
        check_meters_and_gardens(message, login)
    else:
        bot.send_message(message.chat.id,
                         'Введена некорректная пара логин/пароль. Для того, чтобы попробовать снова введите любой текст')


def check_meters_and_gardens(message, login):
    if garden_is_exist(login):
        garden_plots_set = garden_plots(login)
        if len(garden_plots_set) > 1:
            garden_choice = 'Показания для какого участка вы хотите добавить?'
            keyboardmain = types.InlineKeyboardMarkup(row_width=1)
            for garden_id, garden in garden_plots_set.items():
                callback_data = 'garden_id_to_meters|' + login + '|' + str(garden_id)
                button = types.InlineKeyboardButton(text=garden,
                                                    callback_data=callback_data)
                keyboardmain.add(button)
            bot.send_message(message.chat.id, garden_choice, reply_markup=keyboardmain)

        else:
            garden_choice = 'Пожалуйста, нажмите на участок и следуйте инструкциям далее'
            keyboardmain = types.InlineKeyboardMarkup(row_width=1)
            for garden_id, garden in garden_plots_set.items():
                callback_data = 'garden_id_to_meters|' + login + '|' + str(garden_id)
                button = types.InlineKeyboardButton(text=garden,
                                                    callback_data=callback_data)
                keyboardmain.add(button)
                callback_data = 'garden_id|' + login + '|' + str(garden_id)
            bot.send_message(message.chat.id, garden_choice, reply_markup=keyboardmain)

    else:
        keyboardmain = types.InlineKeyboardMarkup(row_width=1)
        data = "garden_registration" + "|" + login
        garden_registration_button = types.InlineKeyboardButton(text="Добавить участок", callback_data=data)
        keyboardmain.add(garden_registration_button)
        bot.send_message(message.chat.id, 'Связанный участок не найден. Пожалуйста, добавьте участок',
                         reply_markup=keyboardmain)


@bot.callback_query_handler(func=lambda call: 'garden_registration' in call.data)
def gardens(call):
    try:
        login = call.data.split('|')[1]
        msg = bot.send_message(call.message.chat.id, 'Пожалуйста, введите адрес участка')
        bot.register_next_step_handler(msg, garden_registration, login)
    except Exception:
        bot.send_message(call.message.chat.id, 'Что-то пошло не так. Пожалуйста попробуйте позже')


@bot.callback_query_handler(func=lambda call: 'garden_id_to_meters' in call.data)
def prepare_to_enter_meters(call):
    try:
        data = call.data.split('|')
        login = data[1]
        garden_id = data[2]
        previous_meters = garden_preivous_meters(login, garden_id)
        info = ""
        for garden_plot, last_meters in previous_meters.items():
            info += f'Предыдущие показания для этого участка -  {last_meters[0]}, были получены {last_meters[1]}\n\n'
        bot.send_message(call.message.chat.id, info)
        # msg = (call.message.chat.id, 'Пожалуйста, введите показания')
        # bot.register_next_step_handler(msg, enter_meters, garden_id, login)
    except Exception:
        bot.send_message(call.message.chat.id, 'Что-то пошло не так. Пожалуйста попробуйте позже')

def enter_meters(message):
    pass

def garden_registration(message, login):
    saved_garden = register_garden(login, adress=message.text)
    if saved_garden:
        adress = saved_garden[0]
        id = saved_garden[1]
        confirmation_request = f'Вы добавили адрес участка: {adress}. Желаете сохранить?'
        keyboardmain = types.InlineKeyboardMarkup(row_width=2)
        garden_registration_confirm_button = types.InlineKeyboardButton(text="Да", callback_data="garden_save_confirm")
        data_to_decline = "garden_save_decline" + "|" + str(id)
        garden_registration_decline_button = types.InlineKeyboardButton(text="Нет", callback_data=data_to_decline)
        keyboardmain.add(garden_registration_confirm_button, garden_registration_decline_button)
        bot.send_message(message.chat.id, confirmation_request, reply_markup=keyboardmain)
    else:
        bot.send_message(message.chat.id, 'Что-то пошло не так, попробуйте ещё раз позже')


@bot.callback_query_handler(func=lambda call: call.data == 'garden_save_confirm')
def confirm_save_garden(call):
    bot.send_message(call.message.chat.id, 'Участок сохранен. Для начала ввода показаний введите любой текст - вы начнете с главного меню')


@bot.callback_query_handler(func=lambda call: 'garden_save_decline' in call.data)
def decline_save_garden(call):
    try:
        id = call.data.split('|')[1]
        delete_garden(id)
        bot.send_message(call.message.chat.id, 'Участок удален')

    except Exception:
        bot.send_message(call.message.chat.id, 'Что-то пошло не так. Пожалуйста попробуйте позже')


def send_notification(chat_id, text):
    bot.send_message(chat_id, text)


bot.polling(none_stop=True)
