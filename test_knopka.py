import telebot
from telebot import types

# Инициализация бота
bot = telebot.TeleBot('7815740376:AAHO-H8mNlVvwA7mZqavDXSa7PXGanEAIDQ')  # Замените на ваш токен

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Кнопка 1", callback_data='button1')
    button2 = types.InlineKeyboardButton("Кнопка 2", callback_data='button2')
    markup.add(button1, button2)

    bot.send_message(message.chat.id, "Добро пожаловать! Выберите кнопку:", reply_markup=markup)

# Обработчик нажатий на инлайн-кнопки
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == 'button1':
        bot.answer_callback_query(call.id, "Вы нажали Кнопку 1!")
        bot.send_message(call.message.chat.id, "Вы выбрали Кнопку 1!")
    elif call.data == 'button2':
        bot.answer_callback_query(call.id, "Вы нажали Кнопку 2!")
        bot.send_message(call.message.chat.id, "Вы выбрали Кнопку 2!")
    else:
        bot.answer_callback_query(call.id, "Неизвестная команда.")

# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)
