# Контрольная работа №3 — FastAPI

**Дисциплина:** Технологии разработки серверных приложений  
**Кафедра:** Индустриального программирования

## Установка и запуск

```bash
# 1. Перейти в папку проекта
cd kr_3

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Создать .env из примера
copy .env.example .env

# 4. Запустить сервер
uvicorn main:app --reload --host 127.0.0.1 --port 8000
# или:
python main.py
```

Сервер запустится на `http://127.0.0.1:8000`

## Переменные окружения

Файл `.env.example` содержит примеры всех переменных. Скопируйте его в `.env` и измените значения. **Не публикуйте `.env`!**

| Переменная | Описание | По умолчанию |
|---|---|---|
| `MODE` | Режим: `DEV` или `PROD` | `DEV` |
| `JWT_SECRET` | Секретный ключ JWT | `my-super-secret-jwt-key-change-in-production` |
| `DOCS_USER` | Логин для `/docs` | `admin` |
| `DOCS_PASSWORD` | Пароль для `/docs` | `docssecret` |

## Тестирование эндпоинтов

### Регистрация и Basic Auth (Задания 6.1–6.2)

```bash
# Регистрация
curl -X POST http://127.0.0.1:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"correctpass"}'

# Вход через Basic Auth
curl -u user1:correctpass http://127.0.0.1:8000/login
```

### JWT Auth (Задания 6.4–6.5)

```bash
# Регистрация (rate limit: 1/мин)
curl -X POST http://127.0.0.1:8000/jwt/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"qwerty123"}'

# Логин → JWT токен (rate limit: 5/мин)
curl -X POST http://127.0.0.1:8000/jwt/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"qwerty123"}'

# Защищённый ресурс
curl http://127.0.0.1:8000/protected_resource \
  -H "Authorization: Bearer <токен>"
```

### RBAC (Задание 7.1)

```bash
# Guest доступ (доступен всем)
curl http://127.0.0.1:8000/rbac/guest \
  -H "Authorization: Bearer <токен>"

# Admin доступ (только admin роль)
curl http://127.0.0.1:8000/rbac/admin \
  -H "Authorization: Bearer <токен>"
```

### SQLite (Задание 8.1)

```bash
# Регистрация в SQLite
curl -X POST http://127.0.0.1:8000/db/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test_user","password":"12345"}'
```

### Todo CRUD (Задание 8.2)

```bash
# Создать
curl -X POST http://127.0.0.1:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy groceries","description":"Milk, eggs, bread"}'

# Получить
curl http://127.0.0.1:8000/todos/1

# Обновить
curl -X PUT http://127.0.0.1:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy groceries","description":"Milk, eggs, bread, cheese","completed":true}'

# Удалить
curl -X DELETE http://127.0.0.1:8000/todos/1
```

### Документация API

- **DEV режим:** `http://127.0.0.1:8000/docs` (требуется Basic Auth из `.env`)
- **PROD режим:** `/docs`, `/redoc`, `/openapi.json` → 404
