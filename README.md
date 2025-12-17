# 🍽️ Cafe Booking Backend

Backend-сервис для бронирования мест в кафе с ролевой моделью пользователей, JWT-аутентификацией и запуском через Docker.

Проект выполнен в рамках дипломной работы.

---

## 🛠️ Технологический стек

- Python 3.11+
- FastAPI
- PostgreSQL 17
- SQLAlchemy 2.0 (async)
- Alembic
- JWT (PyJWT)
- Docker / Docker Compose
- Pytest

---

## 👤 Пользователи и роли

В системе используется ролевая модель доступа:

| Роль | Описание |
|-----|----------|
| USER | Обычный пользователь |
| MANAGER | Менеджер кафе |
| ADMIN | Администратор системы |

Права доступа реализованы через зависимости FastAPI и бизнес-логику менеджеров.

---

## 🔐 Аутентификация

Используется JWT-аутентификация.

### Логин
```
POST /auth/login
```

### Регистрация
```
POST /auth/register
```

JWT-токен необходимо передавать в заголовке:
```
Authorization: Bearer <token>
```

---

## 🙋 Работа с пользователем

### Получить текущего пользователя
```
GET /users/me
```

### Обновить текущего пользователя
```
PATCH /users/me
```

Пользователь может изменять **только свои данные**.
Изменение роли запрещено.

---

## 👥 Административные эндпоинты

Доступны только для ролей `ADMIN` и `MANAGER`.

### Получить список пользователей
```
GET /users/
```

### Получить пользователя по ID
```
GET /users/{user_id}
```

### Обновить пользователя
```
PATCH /users/{user_id}
```

Изменение роли доступно **только администратору**.

---

## 🐳 Запуск проекта через Docker

### 1️⃣ Создать `.env`

```env
APP_TITLE=Бронирование мест в кафе
APP_DESC=Сервис бронирования мест в кафе

POSTGRES_USER=username
POSTGRES_PASSWORD=password
POSTGRES_DB=cafe_db
POSTGRES_HOST=db
POSTGRES_PORT=5432

SECRET=SUPER_SECRET_KEY
FIRST_SUPERUSER_EMAIL=superuser@example.com
FIRST_SUPERUSER_PASSWORD=super_password

ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

### 2️⃣ Запуск контейнеров

```bash
docker compose up --build
```

Будут запущены:
- PostgreSQL
- Alembic migrations
- FastAPI backend

---

### 3️⃣ Доступ к API

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

---

## 🧪 Запуск тестов локально

```bash
python -m pytest .
```

Тесты покрывают:
- аутентификацию
- ролевую модель
- ограничения доступа

---

# Шаблон для проектов со стилизатором Ruff

## Основное

1. Базовая версия Python - 3.11.
2. В файле `requirements_style.txt` находятся зависимости для стилистики.
3. В каталоге `src` находится базовая структура проекта
4. В файле `srd/requirements.txt` прописываются базовые зависимости.
5. В каталоге `infra` находятся настроечные файлы проекта. Здесь же размещать файлы для docker compose.

## Стилистика

Для стилизации кода используется пакеты `Ruff` и `Pre-commit`

Проверка стилистики кода осуществляется командой
```shell
ruff check
```

Если одновременно надо пофиксить то, что можно поиксить автоматически, то добавляем параметр `--fix`
```shell
ruff check --fix
```

Что бы стилистика автоматически проверялась и поправлялась при комитах надо добавить hook pre-commit к git

```shell
pre-commit install
```
