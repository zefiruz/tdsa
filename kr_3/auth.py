import os
import jwt
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

from models import UserInDB

# ============================================================
# Задание 6.2: PassLib CryptContext с bcrypt
# ============================================================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================
# Задание 6.1: HTTP Basic Auth
# ============================================================
basic_security = HTTPBasic()

# ============================================================
# Задание 6.4: JWT
# ============================================================
jwt_security = HTTPBearer(auto_error=False)

SECRET_KEY = os.getenv("JWT_SECRET", "my-super-secret-jwt-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ============================================================
# Задание 6.2: In-memory БД пользователей
# ============================================================
fake_users_db: dict[str, UserInDB] = {}


# ============================================================
# Задание 6.2: Функция auth_user
# ============================================================
def auth_user(
    credentials: HTTPBasicCredentials = Depends(basic_security),
) -> UserInDB:
    """
    Извлекает username и password из заголовка Authorization через HTTPBasicCredentials.
    Находит пользователя в in-memory базе fake_users_db.
    Проверяет корректность пароля с помощью verify из CryptContext.
    Для сравнения логин-строк использует secrets.compare_digest().
    При успехе возвращает объект юзера. При неудаче — HTTPException 401 + WWW-Authenticate: Basic.
    """
    user = fake_users_db.get(credentials.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    # Безопасное сравнение username через secrets.compare_digest
    if not secrets.compare_digest(credentials.username, user.username):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    # Проверка пароля через passlib CryptContext
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return user


# ============================================================
# Задание 6.3: Docs Basic Auth
# ============================================================
docs_security = HTTPBasic(auto_error=False)


def authenticate_docs(credentials: Optional[HTTPBasicCredentials] = Depends(docs_security)):
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Basic"},
        )

    docs_user = os.getenv("DOCS_USER", "admin")
    docs_password = os.getenv("DOCS_PASSWORD", "docssecret")

    if not secrets.compare_digest(credentials.username, docs_user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid docs credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    if not secrets.compare_digest(credentials.password, docs_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid docs credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username


# ============================================================
# Задание 6.4: JWT helpers
# ============================================================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


# ============================================================
# Задание 6.4: JWT Auth dependency
# ============================================================
async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(jwt_security)) -> dict:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(credentials.credentials)
    username: str = payload.get("sub")
    role: str = payload.get("role", "user")
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    return {"username": username, "role": role}


# ============================================================
# Задание 7.1: RBAC dependency
# ============================================================
def require_role(required_role: str):
    """
    Зависимость для проверки роли.
    Иерархия: admin (2) > user (1) > guest (0)
    """
    role_hierarchy = {"guest": 0, "user": 1, "admin": 2}

    def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role", "guest")
        if role_hierarchy.get(user_role, 0) < role_hierarchy.get(required_role, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user_role}' is not sufficient. Required: '{required_role}'",
            )
        return current_user

    return role_checker
