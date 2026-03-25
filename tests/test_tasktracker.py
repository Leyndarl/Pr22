"""
Тесты для TaskTracker (без GUI)
"""

import pytest
import sys
import os
import json
import tempfile
import shutil

# Добавляем путь к корневой папке проекта (на уровень выше)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from taskmanager import TaskManager


class TestTaskManager:

    @pytest.fixture
    def manager(self):
        """Создаёт менеджер задач с временными файлами"""
        # Создаём временную папку
        temp_dir = tempfile.mkdtemp()
        users_file = os.path.join(temp_dir, "users.json")
        tasks_file = os.path.join(temp_dir, "tasks.json")

        manager = TaskManager(users_file, tasks_file)

        yield manager

        # Удаляем временную папку
        shutil.rmtree(temp_dir)

    def test_register_success(self, manager):
        """TC-01: Успешная регистрация"""
        success, message = manager.register("testuser", "password123")

        assert success is True
        assert "зарегистрирован" in message
        assert "testuser" in manager.users

    def test_register_short_password(self, manager):
        """TC-02: Регистрация с коротким паролем"""
        success, message = manager.register("testuser", "123")

        assert success is False
        assert "4 символов" in message

    def test_register_duplicate(self, manager):
        """TC-03: Регистрация существующего пользователя"""
        manager.register("testuser", "password123")
        success, message = manager.register("testuser", "newpass")

        assert success is False
        assert "существует" in message

    def test_login_success(self, manager):
        """TC-04: Успешный вход"""
        manager.register("testuser", "password123")
        success, message = manager.login("testuser", "password123")

        assert success is True
        assert manager.current_user == "testuser"

    def test_login_wrong_password(self, manager):
        """TC-05: Вход с неверным паролем"""
        manager.register("testuser", "password123")
        success, message = manager.login("testuser", "wrongpass")

        assert success is False
        assert manager.current_user is None

    def test_login_nonexistent_user(self, manager):
        """TC-06: Вход несуществующего пользователя"""
        success, message = manager.login("unknown", "pass")

        assert success is False
        assert manager.current_user is None

    def test_add_task_success(self, manager):
        """TC-07: Успешное создание задачи"""
        manager.register("testuser", "pass")
        manager.login("testuser", "pass")

        success, message = manager.add_task("Купить хлеб")

        assert success is True
        assert len(manager.tasks) == 1
        assert manager.tasks[0]["title"] == "Купить хлеб"

    def test_add_task_empty_title(self, manager):
        """TC-08: Создание задачи с пустым названием"""
        manager.register("testuser", "pass")
        manager.login("testuser", "pass")

        success, message = manager.add_task("")

        assert success is False
        assert "пустым" in message

    def test_add_task_without_login(self, manager):
        """TC-09: Создание задачи без входа"""
        success, message = manager.add_task("Задача")

        assert success is False
        assert "войдите" in message

    def test_delete_task_success(self, manager):
        """TC-10: Успешное удаление задачи"""
        manager.register("testuser", "pass")
        manager.login("testuser", "pass")
        manager.add_task("Задача 1")

        success, message = manager.delete_task(0)

        assert success is True
        assert len(manager.tasks) == 0

    def test_delete_nonexistent_task(self, manager):
        """TC-11: Удаление несуществующей задачи"""
        manager.register("testuser", "pass")
        manager.login("testuser", "pass")

        success, message = manager.delete_task(999)

        assert success is False
        assert "не найдена" in message

    def test_mark_done_success(self, manager):
        """TC-12: Отметка задачи как выполненной"""
        manager.register("testuser", "pass")
        manager.login("testuser", "pass")
        manager.add_task("Задача 1")

        success, message = manager.mark_done(0)

        assert success is True
        assert manager.tasks[0]["done"] is True

    def test_get_tasks_for_current_user(self, manager):
        """TC-13: Получение задач текущего пользователя"""
        manager.register("user1", "pass")
        manager.login("user1", "pass")
        manager.add_task("Задача user1")

        manager.logout()
        manager.register("user2", "pass")
        manager.login("user2", "pass")
        manager.add_task("Задача user2")

        tasks = manager.get_tasks_for_current_user()

        assert len(tasks) == 1
        assert tasks[0]["user"] == "user2"