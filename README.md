# PromptBench

PromptBench — это система для сбора запросов к LLM в формате JSON, получения ответов и их сохранения в формате JSON. Предназначен для анализа промптов, параметров и выявления оптимальных вариантов.

## Назначение

Анализ промптов, параметров и выявление оптимального варианта через систематическое тестирование различных конфигураций запросов к языковым моделям.

## Технологический стек

- **FastAPI** — современный веб-фреймворк для создания API
- **Pydantic** — валидация данных и сериализация
- **Uvicorn** — ASGI-сервер
- **Файловая система** — единственный источник истины (директория `STORAGE`)

## Особенности

- **Структура хранения** — данные организованы по схеме:
  - `<test_id>/` — директория теста (это же `id`, и это же `name`)
  - `<test_id>/requests/<request_id>.json` — файл запроса
  - `<test_id>/responses/response_<request_id>.json` — файл ответа
  - `<test_id>/responses/response_<request_id>.error.json` — файл ошибки (если запрос упал)
  - `<test_id>/.running` — маркер выполняющегося теста
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
  "id": "test_1",
  "name": "test_1",
  "status": "created"
}
```

### 2. Добавление запросов

```bash
curl -X POST http://localhost:8020/tests/test_1/requests \
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
curl -X POST http://localhost:8020/tests/test_1/run
```

### 4. Отслеживание прогресса

```bash
curl http://localhost:8020/tests/test_1/progress
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
│   │   ├── 9c2f4a2e5d6b7a10.json
│   │   ├── 1a2b3c4d5e6f7788.json
│   │   └── ...
│   └── responses/
│       ├── response_9c2f4a2e5d6b7a10.json
│       ├── response_1a2b3c4d5e6f7788.json
│       └── ...
├── test_2/
│   └── ...
```

## Разработка

### Логирование

Логи записываются в `/logs/` и выводятся в консоль.

