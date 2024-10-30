import os
import threading
import telebot
from telebot import types
from poisk_tovara import plot_price_history_by_articul, search_products
import re

# Инициализация бота
bot = telebot.TeleBot('7702548527:AAH-xkmHniF9yw09gDtN_JX7tleKJLJjr4E')  # Замените на ваш токен

@bot.message_handler(commands=['start', 'restart'])
def send_welcome(message):
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
        search_products(message.text, message.chat.id, bot)
        search_loop(message)

@bot.message_handler(regexp=r'^/price_chart_.+')
def plot_price_chart(message):
    match = re.match(r'/price_chart_(.+)', message.text)
    if match:
        product_id = re.sub(r'^https?://[^/]+', '', match.group(1))
        plot_price_history_by_articul(bot, message.chat.id, product_id)
    else:
        bot.send_message(message.chat.id, "Некорректная команда.")

def run_bot():
    bot.polling(none_stop=True)

bot_thread = threading.Thread(target=run_bot)
bot_thread.start()
