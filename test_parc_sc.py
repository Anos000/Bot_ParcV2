import requests
import tkinter as tk
from tkinter import messagebox

# Конфигурация GitHub
GITHUB_TOKEN = "your_github_token"  # Личный токен GitHub
REPO_OWNER = "your_username"  # Владелец репозитория
REPO_NAME = "your_repository"  # Название репозитория
WORKFLOW_FILE = "run-all-parsers-sequentially.yml"  # Имя YAML-файла
BRANCH = "main"  # Ветка для запуска


# Функция запуска воркфлоу
def trigger_workflow():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/{WORKFLOW_FILE}/dispatches"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {"ref": BRANCH}

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 204:
            messagebox.showinfo("Успех", "Парсинг запущен на GitHub!")
        else:
            messagebox.showerror("Ошибка", f"Не удалось запустить парсинг: {response.status_code}\n{response.text}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")


# Создаём интерфейс Tkinter
root = tk.Tk()
root.title("Управление парсингом")

# Кнопка для запуска
btn_start = tk.Button(root, text="Запустить парсинг", command=trigger_workflow, bg="green", fg="white",
                      font=("Arial", 14))
btn_start.pack(pady=20)

# Запуск интерфейса
root.mainloop()
