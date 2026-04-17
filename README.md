# PromptBench

PromptBench — это система для сбора запросов к LLM в формате JSON, получения ответов и их сохранения в формате JSON. Предназначен для анализа промптов, параметров и выявления оптимальных вариантов.

## Назначение

Анализ промптов, параметров и выявление оптимального варианта через систематическое тестирование различных конфигураций запросов к языковым моделям.

## Технологический стек

- **FastAPI** — современный веб-фреймворк для создания API
- **Pydantic** — валидация данных и сериализация
- **Uvicorn** — ASGI-сервер
- **SQLAlchemy** — ORM для работы с базой данных
- **SQLite** — база данных
- **Alembic** — управление миграциями базы данных

## Особенности

- **Структура хранения** — данные организованы по схеме:
  - `test_{id}/` — директория теста
  - `test_{id}/requests/request_{id}.json` — файл запроса
  - `test_{id}/responses/response_{id}.json` — файл ответа
- **Асинхронная обработка** — поддержка конкурентной обработки запросов
- **WebSocket** — отслеживание прогресса выполнения тестов в реальном времени
- **Чистая архитектура** — разделение на domain, infrastructure, application, interfaces слои

## Структура проекта

```
backend/
├── src/
│   ├── application/          # Бизнес-логика
│   │   └── services/
│   │       ├── test_service.py       # Создание тестов
│   │       ├── run_test_service.py  # Запуск тестов
│   │       └── websocket.py         # WebSocket для прогресса
│   ├── core/                 # Ядро приложения
│   │   ├── config.py                # Конфигурация
│   │   ├── database.py              # Настройка БД
│   │   └── logger.py                # Логирование
│   ├── domain/               # Доменная модель
│   │   ├── models/
│   │   │   ├── test.py            # Модель Test
│   │   │   ├── request.py          # Модель Request
│   │   │   └── response.py         # Модель Response
│   │   └── enums.py                # Перечисления (TestStatus, RequestStatus)
│   ├── infrastructure/       # Инфраструктура
│   │   ├── repositories/
│   │   │   ├── test_repository.py   # Репозиторий Test
│   │   │   └── request_repository.py # Репозиторий Request
│   │   ├── storage/
│   │   │   └── local.py             # Локальное хранилище JSON
│   │   └── llm/
│   │       └── mock_client.py       # Mock-клиент LLM
│   ├── interfaces/           # Интерфейсы (API)
│   │   ├── api/
│   │   │   └── endpoints/
│   │   │       └── tests.py         # Эндпоинты API
│   │   └── schemas/
│   │       ├── test.py              # Схемы Test
│   │       ├── request.py           # Схемы Request
│   │       └── response.py          # Схемы Response
│   ├── migrations/           # Миграции Alembic
│   └── main.py               # Точка входа приложения
├── storage/                 # Хранилище JSON файлов
├── alembic.ini             # Конфигурация Alembic
├── requirements.txt        # Зависимости Python
├── Dockerfile             # Конфигурация Docker
└── README.md              # Документация
```

## Установка

### Требования

- Python 3.12+
- pip

### Шаги установки

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd PromptBench/backend
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Скопируйте файл конфигурации:
```bash
cp .env.example .env
```

5. Настройте переменные окружения в `.env`:
```env
IS_PRODUCTION=false
STORAGE=./storage
```

## Настройка базы данных

### Применение миграций

Для создания базы данных и применения миграций:

```bash
alembic upgrade head
```

### Создание новой миграции (не требуется, миграция уже создана)

```bash
alembic revision --autogenerate -m "description"
```

## Запуск приложения

### Локальный запуск с помощью Uvicorn

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8020 --reload
```

Приложение будет доступно по адресу: `http://localhost:8020`


## API документация

После запуска приложения доступна интерактивная документация:
- Swagger UI: `http://localhost:8020/docs`
- ReDoc: `http://localhost:8020/redoc`

## Эндпоинты API

### Тесты

#### Создать тест
```http
POST /tests
Content-Type: application/json

{
  "name": "Тест 1"
}
```

#### Получить тест по ID
```http
GET /tests/{test_id}
```

#### Получить список всех тестов
```http
GET /tests
```

#### Удалить тест
```http
DELETE /tests/{test_id}
```

### Запросы

#### Создать запрос для теста
```http
POST /tests/{test_id}/requests
Content-Type: application/json

{
  "payload": {
  "model": "qwen3.5:27b",
  "messages": [
    { "role": "system", "content": "Ты эксперт по Отвечай кратко и только кодом." },
    { "role": "user", "content": "Как объединить два словаря?" }
  ],
  "stream": false,
  "options": { "temperature": 0.2, "num_ctx": 2048 }
  }
}
```

### Запуск тестов

#### Запустить тест
```http
POST /tests/{test_id}/run
```

#### Получить прогресс выполнения
```http
GET /tests/{test_id}/progress
```

#### WebSocket для отслеживания прогресса
```
WS /tests/ws/{test_id}
```

### Health check

```http
GET /healthcheck
```

## Статусы

### Статусы теста (TestStatus)
- `created` — тест создан
- `running` — тест выполняется
- `completed` — тест завершен успешно
- `failed` — тест завершен с ошибкой

### Статусы запроса (RequestStatus)
- `pending` — запрос ожидает обработки
- `sent` — запрос отправлен
- `done` — запрос выполнен успешно
- `failed` — запрос завершен с ошибкой

## Пример использования

### 1. Создание теста

```bash
curl -X POST http://localhost:8020/tests \
  -H "Content-Type: application/json" \
  -d '{"name": "Тест 1"}'
```

Ответ:
```json
{
  "id": 1,
  "name": "Тест 1",
  "status": "created"
}
```

### 2. Добавление запросов

```bash
curl -X POST http://localhost:8020/tests/1/requests \
  -H "Content-Type: application/json" \
  -d '{
          "payload": {
          "model": "qwen3.5:27b",
          "messages": [
            { "role": "system", "content": "Ты эксперт по Python. Отвечай кратко и только кодом." },
            { "role": "user", "content": "Как объединить два словаря?" }
          ],
          "stream": false,
          "options": { "temperature": 0.2, "num_ctx": 2048 }
          }
        }'
```

### 3. Запуск теста

```bash
curl -X POST http://localhost:8020/tests/1/run
```

### 4. Отслеживание прогресса

```bash
curl http://localhost:8020/tests/1/progress
```

Ответ:
```json
{
  "total": 10,
  "done": 5,
  "failed": 0,
  "pending": 5
}
```

## Хранение данных

Данные хранятся в локальной файловой системе в директории, указанной в переменной `STORAGE` (по умолчанию `./storage`).

Структура:
```
storage/
├── test_1/
│   ├── requests/
│   │   ├── request_1.json
│   │   ├── request_2.json
│   │   └── ...
│   └── responses/
│       ├── response_1.json
│       ├── response_2.json
│       └── ...
├── test_2/
│   └── ...
```

## Разработка

### Добавление новой модели

1. Создайте модель в `src/domain/models/`
2. Создайте схему в `src/interfaces/schemas/`
3. Создайте репозиторий в `src/infrastructure/repositories/`
4. Создайте эндпоинт в `src/interfaces/api/endpoints/`
5. Создайте миграцию: `alembic revision --autogenerate -m "description"`

### Логирование

Логи записываются в `src/logs/` и выводятся в консоль.

