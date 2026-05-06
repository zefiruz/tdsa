from pydantic import BaseModel, EmailStr, conint, constr
from typing import Optional

# Модель ответа об ошибке (Задание 10.1)
class ErrorResponse(BaseModel):
    detail: str

# Модель пользователя с валидацией (Задание 10.2)
class UserRegister(BaseModel):
    username: str
    age: conint(gt=18)
    email: EmailStr
    password: constr(min_length=8, max_length=16)
    phone: Optional[str] = 'Unknown'

# Модели для in-memory хранилища (Задание 11.2)
class UserIn(BaseModel):
    username: str
    age: int

class UserOut(BaseModel):
    id: int
    username: str
    age: int