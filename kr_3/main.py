import os
import secrets
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from models import (
    User, UserInDB, Token, LoginRequest, Message,
    Todo, TodoCreate, TodoUpdate,
)
from auth import (
    fake_users_db,
    hash_password,
    verify_password,
    auth_user,
    authenticate_docs,
    create_access_token,
    get_current_user,
    require_role,
    SECRET_KEY,
)
from database import (
    insert_user,
    get_user_by_username,
    create_todo,
    get_todo,
    update_todo,
    delete_todo,
)

# Задание 6.3: MODE конфигурация
MODE = os.getenv("MODE", "DEV").upper()

if MODE not in ("DEV", "PROD"):
    MODE = "DEV"  # fallback по заданию

# Rate Limiter (задание 6.5)

limiter = Limiter(key_func=get_remote_address)


# Задание 6.3: Создание приложения
if MODE == "PROD":
    # PROD: вся документация отключена, возвращается 404
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    @app.get("/docs", include_in_schema=False)
    async def docs_prod():
        raise HTTPException(status_code=404, detail="Not found")

    @app.get("/redoc", include_in_schema=False)
    async def redoc_prod():
        raise HTTPException(status_code=404, detail="Not found")

    @app.get("/openapi.json", include_in_schema=False)
    async def openapi_prod():
        raise HTTPException(status_code=404, detail="Not found")

elif MODE == "DEV":
    # DEV: /docs и /openapi.json защищены Basic Auth, /redoc скрыт
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    @app.get("/docs", include_in_schema=False)
    async def get_documentation(_=Depends(authenticate_docs)):
        from fastapi.openapi.utils import get_openapi
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            routes=app.routes,
        )
        return get_swagger_ui_html(openapi_url="/openapi.json", title="Docs")

    @app.get("/openapi.json", include_in_schema=False)
    async def get_openapi_json(_=Depends(authenticate_docs)):
        from fastapi.openapi.utils import get_openapi
        return get_openapi(
            title=app.title,
            version=app.version,
            routes=app.routes,
        )

else:
    # Неизвестный MODE — стандартный FastAPI
    app = FastAPI()


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests"},
    )


# Задание 6.2: /register (POST) и /login (GET) — Basic Auth

@app.post("/register", response_model=Message, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: User):
    if user_data.username in fake_users_db:
        raise HTTPException(status_code=409, detail="User already exists")

    hashed_pw = hash_password(user_data.password)
    user_in_db = UserInDB(username=user_data.username, hashed_password=hashed_pw)
    fake_users_db[user_data.username] = user_in_db
    return {"message": f"User {user_data.username} registered successfully"}


@app.get("/login")
async def login(current_user: UserInDB = Depends(auth_user)):
    return {"message": f"Welcome, {current_user.username}!"}


# Задание 6.4-6.5: JWT — POST /login, POST /register, /protected_resource

@app.post("/jwt/register", response_model=Message, status_code=status.HTTP_201_CREATED)
@limiter.limit("1/minute")
async def jwt_register(request: Request, user_data: User):
    if user_data.username in fake_users_db:
        raise HTTPException(status_code=409, detail="User already exists")

    hashed_pw = hash_password(user_data.password)
    user_in_db = UserInDB(username=user_data.username, hashed_password=hashed_pw, role="user")
    fake_users_db[user_data.username] = user_in_db
    return {"message": "New user created"}


@app.post("/jwt/login", response_model=Token)
@limiter.limit("5/minute")
async def jwt_login(request: Request, credentials: LoginRequest):
    # Проверка существования через secrets.compare_digest
    user = None
    for uname in fake_users_db:
        if secrets.compare_digest(uname, credentials.username):
            user = fake_users_db[uname]
            break

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Authorization failed")

    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return Token(access_token=access_token)


@app.get("/protected_resource")
async def protected_resource(current_user: dict = Depends(get_current_user)):
    return {"message": "Access granted", "user": current_user["username"]}


@app.get("/jwt/me")
async def jwt_me(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"], "role": current_user["role"]}


# Задание 7.1: RBAC

@app.get("/rbac/admin")
async def admin_endpoint(_=Depends(require_role("admin"))):
    return {"role": "admin", "message": "Full admin access granted — CRUD permissions"}


@app.get("/rbac/user")
async def user_endpoint(_=Depends(require_role("user"))):
    return {"role": "user", "message": "Standard user access — read and update permissions"}


@app.get("/rbac/guest")
async def guest_endpoint(_=Depends(require_role("guest"))):
    return {"role": "guest", "message": "Read-only guest access"}


# Задание 8.1: SQLite — POST /register (в БД)

@app.post("/db/register", response_model=Message)
async def db_register(user_data: User):
    existing = get_user_by_username(user_data.username)
    if existing:
        raise HTTPException(status_code=409, detail="Username already exists in database")

    user_id = insert_user(user_data.username, user_data.password)
    return {"message": "User registered successfully!"}


@app.get("/db/users")
async def db_list_users(current_user: dict = Depends(require_role("admin"))):
    from database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users")
    rows = [{"id": row["id"], "username": row["username"]} for row in cursor.fetchall()]
    conn.close()
    return {"users": rows}


# Задание 8.2: CRUD для Todo

@app.post("/todos", response_model=Todo, status_code=status.HTTP_201_CREATED)
async def create_new_todo(todo_data: TodoCreate):
    return create_todo(
        title=todo_data.title,
        description=todo_data.description,
        completed=False,
    )


@app.get("/todos/{todo_id}", response_model=Todo)
async def read_todo(todo_id: int):
    todo = get_todo(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.put("/todos/{todo_id}", response_model=Todo)
async def update_existing_todo(todo_id: int, todo_data: TodoUpdate):
    updated = update_todo(
        todo_id,
        title=todo_data.title,
        description=todo_data.description,
        completed=todo_data.completed,
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated


@app.delete("/todos/{todo_id}")
async def delete_existing_todo(todo_id: int):
    if not delete_todo(todo_id):
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted successfully"}


# ============================================================
# Health check
# ============================================================

@app.get("/health")
async def health():
    return {"status": "ok", "mode": MODE}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
