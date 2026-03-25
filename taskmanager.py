"""
Модуль с бизнес-логикой TaskTracker (без GUI)
"""

import json
import os


class TaskManager:
    """Класс для управления задачами (без GUI)"""

    def __init__(self, users_file="data/users.json", tasks_file="data/tasks.json"):
        self.users_file = users_file
        self.tasks_file = tasks_file
        self.current_user = None
        self.users = {}
        self.tasks = []
        self.load_data()

    def load_data(self):
        """Загружает данные из файлов"""
        if os.path.exists(self.users_file):
            with open(self.users_file, "r", encoding="utf-8") as f:
                self.users = json.load(f)
        else:
            self.users = {}

        if os.path.exists(self.tasks_file):
            with open(self.tasks_file, "r", encoding="utf-8") as f:
                self.tasks = json.load(f)
        else:
            self.tasks = []

    def save_users(self):
        """Сохраняет пользователей в файл"""
        with open(self.users_file, "w", encoding="utf-8") as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)

    def save_tasks(self):
        """Сохраняет задачи в файл"""
        with open(self.tasks_file, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

    def register(self, login, password):
        """
        Регистрация нового пользователя

        Returns:
            tuple: (success, message)
        """
        if not login or not password:
            return False, "Логин и пароль не могут быть пустыми"

        if len(password) < 4:
            return False, "Пароль должен быть не менее 4 символов"

        if login in self.users:
            return False, "Пользователь уже существует"

        self.users[login] = password
        self.save_users()
        return True, "Пользователь зарегистрирован"

    def login(self, login, password):
        """
        Вход пользователя

        Returns:
            tuple: (success, message)
        """
        if login not in self.users:
            return False, "Пользователь не найден"

        if self.users[login] != password:
            return False, "Неверный пароль"

        self.current_user = login
        return True, "Вход выполнен"

    def add_task(self, title):
        """
        Добавление задачи

        Returns:
            tuple: (success, message)
        """
        if not self.current_user:
            return False, "Сначала войдите в систему"

        if not title or title.strip() == "":
            return False, "Название задачи не может быть пустым"

        task = {"user": self.current_user, "title": title, "done": False}
        self.tasks.append(task)
        self.save_tasks()
        return True, "Задача добавлена"

    def delete_task(self, index):
        """
        Удаление задачи по индексу

        Returns:
            tuple: (success, message)
        """
        if not self.current_user:
            return False, "Сначала войдите в систему"

        if index < 0 or index >= len(self.tasks):
            return False, "Задача не найдена"

        # Проверяем, что задача принадлежит текущему пользователю
        if self.tasks[index]["user"] != self.current_user:
            return False, "Нельзя удалить чужую задачу"

        del self.tasks[index]
        self.save_tasks()
        return True, "Задача удалена"

    def mark_done(self, index):
        """
        Отметка задачи как выполненной

        Returns:
            tuple: (success, message)
        """
        if not self.current_user:
            return False, "Сначала войдите в систему"

        if index < 0 or index >= len(self.tasks):
            return False, "Задача не найдена"

        if self.tasks[index]["user"] != self.current_user:
            return False, "Нельзя отметить чужую задачу"

        self.tasks[index]["done"] = True
        self.save_tasks()
        return True, "Задача отмечена как выполненная"

    def get_tasks_for_current_user(self):
        """Возвращает задачи текущего пользователя"""
        if not self.current_user:
            return []

        return [t for t in self.tasks if t["user"] == self.current_user]

    def get_all_tasks(self):
        """Возвращает все задачи"""
        return self.tasks

    def logout(self):
        """Выход из системы"""
        self.current_user = None
        return True, "Выход выполнен"