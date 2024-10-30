import os
import threading
import telebot
from telebot import types
from poisk_tovara import plot_price_history_by_articul, search_products
import re
from reges_users import register_user

# Инициализация бота
bot = telebot.TeleBot('7702548527:AAH-xkmHniF9yw09gDtN_JX7tleKJLJjr4E')  # Замените на ваш токен

@bot.message_handler(commands=['start', 'restart'])
def send_welcome(message):
    register_user(message)  # Регистрация пользователя
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add("Динамика цены товара", "Поиск товара")
    bot.send_message(message.chat.id, "Выберите опцию из меню:", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == "Поиск товара":
        search_loop(message)
    elif message.text == "Назад":
        send_welcome(message)

def search_loop(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add("Назад")
    bot.send_message(message.chat.id, "Введите запрос для поиска или нажмите 'Назад' для возврата.", reply_markup=markup)
    bot.register_next_step_handler(message, search_product_by_title_handler)

def search_product_by_title_handler(message):
    if message.text == "Назад":
        send_welcome(message)
    else:
        search_products(message.text, message.chat.id, bot)  # Здесь происходит поиск
        search_loop(message)  # Возвращаемся к поиску после завершения

@bot.callback_query_handler(func=lambda call: call.data.startswith("grapic_"))
def callback_query(call):
    product_id = call.data.split("_")[1]
    plot_price_history_by_articul(bot, call.message.chat.id, product_id)  # Построение графика по артикулу

def run_bot():
    bot.polling(none_stop=True)

bot_thread = threading.Thread(target=run_bot)
bot_thread.start()
