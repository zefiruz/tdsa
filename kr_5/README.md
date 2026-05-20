# Task Manager API

Серверное приложение для управления задачами и обмена сообщениями через WebSocket, разработанное на FastAPI

## 🚀 Инструкция по запуску проекта

### 1. Локальный запуск приложения

     ```powershell
     python -m venv .venv
     .venv\Scripts\activate
     ```

   ```bash
   pip install -r requirements.txt
   ```

   ```bash
   uvicorn app.main:app --reload
   ```
   [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 2. Запуск интеграционных тестов

```bash
python -m pytest
```

### 3. Запуск внутри Docker-контейнера

```bash
docker compose up --build
```

#### Проверка состояния после запуска контейнера:
```bash
curl http://localhost:8000/health
```