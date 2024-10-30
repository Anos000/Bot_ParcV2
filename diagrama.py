import pandas as pd
import matplotlib.pyplot as plt
import os
import re  # Импортируем модуль для регулярных выражений
from io import BytesIO  # Импортируем BytesIO для отправки графиков
import matplotlib

matplotlib.use('Agg')  # Установите режим 'Agg' для рисования в памяти

# Функция для очистки цен, оставляя только рубли
def clean_price(price):
    if isinstance(price, str):
        # Убираем все символы, кроме цифр и запятых
        price = re.sub(r'[^\d,]', '', price)

        # Если запятая найдена, убираем её и всё после неё
        if ',' in price:
            price = price.split(',')[0]  # Берём только рубли
    return float(price) if price else None

# Функция для поиска артикулов в файлах и построения графиков
def plot_price_history_by_articul(articul, chat_id, bot):
    # Список файлов Excel для поиска с указанием имён
    excel_files = [
        ("downloads/parsed_data.xlsx", "File 1"),
        ("downloads/parsed_data2.xlsx", "File 2"),
        ("downloads/parsed_data_autoopt.xlsx", "File 3")
    ]

    # Словарь для хранения данных по каждому файлу
    data_by_file = {}
    product_names_by_file = {}  # Для хранения названий товаров
    selected_name = None  # Инициализация переменной

    # Проход по каждому файлу
    for file_name, label in excel_files:
        if os.path.exists(file_name):
            df = pd.read_excel(file_name)

            # Проверяем наличие необходимых колонок
            if 'Артикул' in df.columns and 'Цена' in df.columns and 'Дата парсинга' in df.columns and 'Название' in df.columns:
                # Фильтрация данных по артикулу и создание копии для предотвращения SettingWithCopyWarning
                articul_data = df[df['Артикул'] == articul].copy()

                if not articul_data.empty:
                    print(f"Найден артикул {articul} в файле {file_name}")

                    # Сохраняем названия товаров
                    unique_names = articul_data['Название'].unique()
                    product_names_by_file[label] = unique_names

                    # Если названий несколько, предлагаем выбрать
                    if len(unique_names) > 1:
                        print(f"Найдены несколько товаров с артикулом {articul} в {file_name}:")
                        for idx, name in enumerate(unique_names, start=1):
                            print(f"{idx}. {name}")

                        choice = int(input(f"Выберите номер товара (1-{len(unique_names)}): ")) - 1
                        selected_name = unique_names[choice]
                    else:
                        # Если уникальных названий только одно, берем его
                        selected_name = unique_names[0]

                    # Фильтруем данные по выбранному товару
                    articul_data = articul_data[articul_data['Название'] == selected_name]

                    # Очищаем цены
                    articul_data['Цена'] = articul_data['Цена'].apply(clean_price)

                    # Фильтруем данные, оставляя только непустые цены
                    articul_data = articul_data[articul_data['Цена'].notnull()]

                    if not articul_data.empty:
                        # Сохраняем данные для каждого файла
                        data_by_file[label] = articul_data[['Дата парсинга', 'Цена']]
                    else:
                        # Отправка сообщения в чат, если нет числовых значений цен
                        bot.send_message(chat_id, f"Нет числовых значений цен для артикула {articul} в файле {file_name}.")
                        print(f"Нет числовых значений цен для артикула {articul} в файле {file_name}.")

    # Если данные найдены, строим графики
    if data_by_file:
        for source, data in data_by_file.items():
            # Используем .loc для преобразования даты
            data.loc[:, 'Дата парсинга'] = pd.to_datetime(data['Дата парсинга'])  # Преобразуем даты

            # Сортируем по дате
            data = data.sort_values(by='Дата парсинга')

            # Построение графика для каждого источника данных
            plt.figure(figsize=(12, 8))
            plt.plot(data['Дата парсинга'], data['Цена'], marker='o', label=source)
            plt.title(f'Изменение цен для артикула {articul} ({selected_name}) в {source}')
            plt.xlabel('Дата')
            plt.ylabel('Цена')

            # Добавление черточек только на осях X и Y
            plt.xticks(rotation=45, ha='right')  # Поворот подписей по оси X для читаемости
            plt.grid(axis='both', linestyle='--', linewidth=0.5)  # Сетка с черточками

            # Настройка параметров осей
            plt.tick_params(axis='y', which='both', direction='in', length=5)  # Установить параметры оси Y

            plt.legend()
            plt.tight_layout()

            # Сохранение графика в буфер
            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)  # Возвращаем указатель в начало буфера
            plt.close()  # Закрываем фигуру

            # Отправка графика в чат
            bot.send_photo(chat_id, photo=buf)
