from fastapi import FastAPI, Request, status, HTTPException, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from itertools import count
from threading import Lock

from .exceptions import CustomExceptionA, CustomExceptionB
from .schemas import ErrorResponse, UserRegister, UserIn, UserOut

app = FastAPI()

# Задание 10.1: Кастомная обработка ошибок

@app.exception_handler(CustomExceptionA)
async def custom_exception_a_handler(request: Request, exc: CustomExceptionA):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message},
    )

@app.exception_handler(CustomExceptionB)
async def custom_exception_b_handler(request: Request, exc: CustomExceptionB):
    return JSONResponse(
        status_code=404,
        content={"detail": exc.message},
    )

@app.get("/trigger-a", response_model=ErrorResponse)
async def trigger_a(condition: bool = False):
    if not condition:
        raise CustomExceptionA("Условие не выполнено (CustomExceptionA)")
    return {"detail": "Success"}

@app.get("/trigger-b/{item_id}", response_model=ErrorResponse)
async def trigger_b(item_id: int):
    if item_id != 1:
        raise CustomExceptionB("Ресурс не найден (CustomExceptionB)")
    return {"detail": "Success"}

# Задание 10.2: Обработка ошибок валидации

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Ошибка валидации входящих данных",
            "errors": exc.errors()
        },
    )

@app.post("/register")
async def register_user(user: UserRegister):
    return {"message": "Пользователь успешно зарегистрирован", "user": user}

# Задание 11.1 и 11.2: Эндпоинты для тестов

db: dict[int, dict] = {}
_id_seq = count(start=1)
_id_lock = Lock()

def next_user_id() -> int:
    with _id_lock:
        return next(_id_seq)

@app.post("/users", response_model=UserOut, status_code=201)
def create_user(user: UserIn):
    user_id = next_user_id()
    db[user_id] = user.model_dump()
    return {"id": user_id, **db[user_id]}

@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    if user_id not in db:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user_id, **db[user_id]}

@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    if db.pop(user_id, None) is None:
        raise HTTPException(status_code=404, detail="User not found")
    return Response(status_code=204)