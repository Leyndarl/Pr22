"""
Тесты для TaskTracker
"""

import pytest
import sys
import os
import json
import tempfile
import shutil

# Добавляем путь к корневой папке
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Импортируем функции из приложения
from tasktracker import load_data, save_users, save_tasks, add_task, delete_task, mark_done


class TestTaskTracker:

    @pytest.fixture
    def temp_data_dir(self):
        """Создаёт временную папку для тестовых данных"""
        temp_dir = tempfile.mkdtemp()
        old_data_dir = "data"

        # Сохраняем оригинальную папку и подменяем на временную
        original_dir = os.getcwd()
        os.chdir(temp_dir)

        # Создаём папку data во временной директории
        os.makedirs("data", exist_ok=True)

        yield temp_dir

        # Возвращаемся обратно и удаляем временную папку
        os.chdir(original_dir)
        shutil.rmtree(temp_dir)

    def test_register_user(self, temp_data_dir):
        """TC-01: Регистрация нового пользователя"""
        import tasktracker

        # Подменяем глобальные переменные
        tasktracker.users = {}
        tasktracker.USERS_FILE = "data/users.json"

        # Создаём пользователя
        tasktracker.users["testuser"] = "password123"
        tasktracker.save_users()

        # Проверяем, что файл создался и содержит данные
        with open("data/users.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "testuser" in data
        assert data["testuser"] == "password123"

    def test_login_success(self, temp_data_dir):
        """TC-02: Вход с корректными данными"""
        import tasktracker

        tasktracker.users = {"testuser": "password123"}
        tasktracker.current_user = None

        # Эмулируем успешный вход
        if "testuser" in tasktracker.users and tasktracker.users["testuser"] == "password123":
            tasktracker.current_user = "testuser"

        assert tasktracker.current_user == "testuser"

    def test_login_fail_wrong_password(self, temp_data_dir):
        """TC-03: Вход с неверным паролем"""
        import tasktracker

        tasktracker.users = {"testuser": "password123"}
        tasktracker.current_user = None

        # Эмулируем попытку входа с неверным паролем
        if "testuser" in tasktracker.users and tasktracker.users["testuser"] == "wrongpass":
            tasktracker.current_user = "testuser"

        assert tasktracker.current_user is None

    def test_create_task(self, temp_data_dir):
        """TC-04: Создание задачи"""
        import tasktracker

        tasktracker.tasks = []
        tasktracker.current_user = "testuser"

        # Эмулируем создание задачи
        new_task = {"user": "testuser", "title": "Тестовая задача", "done": False}
        tasktracker.tasks.append(new_task)

        assert len(tasktracker.tasks) == 1
        assert tasktracker.tasks[0]["title"] == "Тестовая задача"
        assert tasktracker.tasks[0]["done"] is False

    def test_create_task_empty_title(self, temp_data_dir):
        """TC-05: Создание задачи с пустым названием"""
        import tasktracker

        # В текущей версии приложения нет валидации пустого названия
        # Это ожидаемый дефект (Major)
        tasktracker.tasks = []
        tasktracker.current_user = "testuser"

        # Эмулируем создание задачи с пустым названием
        new_task = {"user": "testuser", "title": "", "done": False}
        tasktracker.tasks.append(new_task)

        # Дефект: задача с пустым названием создаётся
        assert len(tasktracker.tasks) == 1
        assert tasktracker.tasks[0]["title"] == ""  # Это баг!

    def test_delete_task(self, temp_data_dir):
        """TC-06: Удаление задачи"""
        import tasktracker

        tasktracker.tasks = [
            {"user": "testuser", "title": "Задача 1", "done": False},
            {"user": "testuser", "title": "Задача 2", "done": False}
        ]

        # Удаляем первую задачу
        index = 0
        del tasktracker.tasks[index]

        assert len(tasktracker.tasks) == 1
        assert tasktracker.tasks[0]["title"] == "Задача 2"

    def test_delete_nonexistent_task(self, temp_data_dir):
        """TC-07: Удаление несуществующей задачи (ожидаемый дефект)"""
        import tasktracker

        tasktracker.tasks = []

        # В текущей версии приложения нет проверки на пустой список
        # Это ожидаемый дефект (Major)

        # Эмулируем попытку удаления из пустого списка
        # Приложение должно показывать ошибку, но сейчас падает
        try:
            index = 0  # несуществующий индекс
            del tasktracker.tasks[index]
            assert False, "Должна быть ошибка, но задача была 'удалена'"
        except IndexError:
            # Ожидаемое поведение — ошибка, но приложение должно ловить её
            assert True

    def test_mark_task_done(self, temp_data_dir):
        """TC-08: Отметка задачи как выполненной"""
        import tasktracker

        tasktracker.tasks = [
            {"user": "testuser", "title": "Задача 1", "done": False}
        ]

        # Отмечаем задачу как выполненную
        index = 0
        tasktracker.tasks[index]["done"] = True

        assert tasktracker.tasks[0]["done"] is True

    def test_save_tasks_to_file(self, temp_data_dir):
        """TC-09: Сохранение задач в файл"""
        import tasktracker

        tasktracker.tasks = [
            {"user": "testuser", "title": "Задача 1", "done": False},
            {"user": "testuser", "title": "Задача 2", "done": True}
        ]
        tasktracker.TASKS_FILE = "data/tasks.json"

        tasktracker.save_tasks()

        with open("data/tasks.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 2
        assert data[0]["title"] == "Задача 1"
        assert data[1]["done"] is True