import mysql.connector
import csv

# Подключение к базе данных MySQL
db_config = {
    'host': 'krutskuy.beget.tech',  # Замените на ваше имя хоста
    'user': 'krutskuy_parc',  # Ваше имя пользователя
    'password': 'AnosVoldigod0',  # Ваш пароль
    'database': 'krutskuy_parc',  # Имя вашей базы данных
}


# Функция для извлечения данных из таблицы и сохранения их в CSV
def export_table_to_csv(table_name, filename, headers):
    # Подключаемся к базе данных
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        print("Подключение к базе данных успешно!")

        # Выполняем запрос к таблице
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        # Сохранение данных в CSV
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)  # Записываем заголовки
            writer.writerows(rows)  # Записываем все строки таблицы

        print(f"Данные из таблицы '{table_name}' сохранены в {filename}")

    except mysql.connector.Error as err:
        print(f"Ошибка подключения: {err}")
    finally:
        # Закрываем соединение с базой данных
        if conn.is_connected():
            cursor.close()
            conn.close()


# Пример использования функции для извлечения данных из таблицы 'productsV3'
export_table_to_csv(
    table_name='productsV3',
    filename='productsV3.csv',
    headers=['ID', 'Дата парсинга', 'Название', 'Артикул', 'Цена', 'Изображение', 'Ссылка']
)

