from pydantic import BaseModel
from typing import Optional


# --- Задание 6.2: Модели пользователей ---

class UserBase(BaseModel):
    username: str


class User(UserBase):
    password: str


class UserInDB(UserBase):
    hashed_password: str
    role: str = "user"


# --- Задание 6.4-6.5: Токен и вспомогательные модели ---

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


class Message(BaseModel):
    message: str


class ErrorDetail(BaseModel):
    detail: str


# --- Задание 8.2: Модель Todo ---

class TodoCreate(BaseModel):
    title: str
    description: str


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class Todo(BaseModel):
    id: int
    title: str
    description: str
    completed: bool = False
