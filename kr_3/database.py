import sqlite3
import os
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Создание таблиц при инициализации."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Задание 8.1: таблица users (id, username, password)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Задание 8.2: таблица todos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# Задание 8.1: Операции с users
# ============================================================

def insert_user(username: str, password: str) -> int:
    """INSERT пользователя в users. commit() обязателен."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, password)
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id


def get_user_by_username(username: str) -> Optional[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


# ============================================================
# Задание 8.2: CRUD для Todo
# ============================================================

def create_todo(title: str, description: str, completed: bool = False) -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO todos (title, description, completed) VALUES (?, ?, ?)",
        (title, description, int(completed))
    )
    conn.commit()
    todo_id = cursor.lastrowid
    conn.close()
    return {"id": todo_id, "title": title, "description": description, "completed": completed}


def get_todo(todo_id: int) -> Optional[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row["id"], "title": row["title"], "description": row["description"], "completed": bool(row["completed"])}
    return None


def update_todo(todo_id: int, title: Optional[str] = None, description: Optional[str] = None, completed: Optional[bool] = None) -> Optional[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()

    # Получаем текущие данные
    cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    new_title = title if title is not None else row["title"]
    new_description = description if description is not None else row["description"]
    new_completed = completed if completed is not None else bool(row["completed"])

    cursor.execute(
        "UPDATE todos SET title = ?, description = ?, completed = ? WHERE id = ?",
        (new_title, new_description, int(new_completed), todo_id)
    )
    conn.commit()
    conn.close()
    return {"id": todo_id, "title": new_title, "description": new_description, "completed": new_completed}


def delete_todo(todo_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


# Инициализация БД при импорте
init_db()
