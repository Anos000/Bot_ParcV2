import os
import subprocess
import threading
import telebot
from telebot import types
from diagrama import plot_price_history_by_articul  # Импорт функции для построения графика
from poisk_tovara import search_products  # Импорт функций для поиска товара
from reges_users import create_tables, add_user  # Импорт функций для регистрации пользователей

# Инициализация бота
bot = telebot.TeleBot('7702548527:AAH-xkmHniF9yw09gDtN_JX7tleKJLJjr4E')  # Замените на свой токен бота

# Глобальные переменные для отслеживания состояния
stop_event = threading.Event()
is_plotting = False  # Флаг для отслеживания процесса построения графика

# Создание таблицы пользователей при запуске
create_tables()

# Функция для приветственного сообщения с кнопкой "Старт/Перезапуск"
@bot.message_handler(commands=['start', 'restart'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)  # Кнопки в один ряд
    item2 = types.KeyboardButton("Динамика цены товара")
    item3 = types.KeyboardButton("Поиск товара")  # Кнопка для поиска товара

    markup.add(item2, item3)
    bot.send_message(message.chat.id, "Выберите опцию из меню:", reply_markup=markup)


# Обработчик текстовых сообщений
@bot.message_handler(content_types=['text'])
def handle_text(message):
    global stop_event, is_plotting

    if is_plotting:
        stop_event.set()  # Останавливаем процесс построения графика
        is_plotting = False
    elif message.text == "Поиск товара":  # Обработчик для поиска товара
        search_loop(message)  # Включаем цикл для режима поиска
    elif message.text == "Назад":
        send_welcome(message)  # Возвращаемся к главному меню


# Цикл поиска товара с кнопкой "Назад"
def search_loop(message):
    # Создаем клавиатуру с кнопкой "Назад"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    back_button = types.KeyboardButton("Назад")
    markup.add(back_button)

    # Входим в цикл ожидания ввода пользователя
    bot.send_message(message.chat.id, "Введите запрос для поиска или нажмите 'Назад' для возврата.", reply_markup=markup)
    bot.register_next_step_handler(message, search_product_by_title_handler)


# Обработчик для поиска по названию
def search_product_by_title_handler(message):
    if message.text == "Назад":  # Условие выхода из режима поиска
        send_welcome(message)
    else:
        query = message.text
        chat_id = message.chat.id
        search_products(query, chat_id, bot)  # Поиск товара
        search_loop(message)  # Повторяем цикл поиска, ожидая нового ввода



# Функция для запуска бота
def run_bot():
    bot.polling(none_stop=True)

# Запуск бота в отдельном потоке
bot_thread = threading.Thread(target=run_bot)
bot_thread.start()
