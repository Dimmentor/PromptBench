## Gateway к оркестратору (для других сервисов)

### 1) Streaming batch (SSE): результаты по мере готовности

```http
POST /gateway/batch/stream
Content-Type: application/json
Accept: text/event-stream
```

Тело (массив):

```json
[
  { "id": 1, "payload": { "model": "qwen3:14b", "messages": [], "stream": false } },
  { "id": 2, "payload": { "model": "qwen3:14b", "messages": [], "stream": false } }
]
```

Ответ: SSE поток событий `data: ...`, где каждое событие — JSON:

```json
{ "id": 1, "payload": {"...":  "..."} }
```

Завершение потока:

```
data: [DONE]
```


### Пример запроса:
```json
[
  {
    "id": 1,
    "payload": {
      "model": "qwen3:14b",
      "messages": [
        {
          "role": "system",
          "content": "Ты эксперт по Python."
        },
        {
          "role": "user",
          "content": "Напиши функцию, которая проверит входящий текст(str) на палиндром, используя оптимальный алгоритм. Объясни свое решение"
        }
      ],
      "stream": false,
      "options": {
        "temperature": 1.2,
        "top_k": 100,
        "top_p": 0.99,
        "tfs_z": 1.0,
        "repeat_penalty": 1.2,
        "repeat_last_n": 64,
        "mirostat": 2,
        "mirostat_tau": 8.0,
        "mirostat_eta": 0.3,
        "num_ctx": 4096,
        "num_predict": 500,
        "seed": 42
      }
    }
  },
  {
    "id": 2,
    "payload": {
      "model": "qwen3:14b",
      "messages": [
        {
          "role": "system",
          "content": "Ты эксперт по Python."
        },
        {
          "role": "user",
          "content": "Напиши функцию, которая проверит входящий текст(str) на палиндром, используя оптимальный алгоритм. Объясни свое решение"
        }
      ],
      "stream": false,
      "options": {
        "temperature": 0.7,
        "top_k": 40,
        "top_p": 0.95,
        "repeat_penalty": 1.1,
        "mirostat": 1,
        "mirostat_tau": 5.0,
        "mirostat_eta": 0.1,
        "num_ctx": 2048
      }
    }
  },
  {
    "id": 3,
    "payload": {
      "model": "qwen3:14b",
      "messages": [
        {
          "role": "system",
          "content": "Ты эксперт по Python."
        },
        {
          "role": "user",
          "content": "Напиши функцию, которая проверит входящий текст(str) на палиндром, используя оптимальный алгоритм. Объясни свое решение"
        }
      ],
      "stream": false,
      "options": {
        "temperature": 0.1,
        "top_k": 10,
        "top_p": 0.9,
        "repeat_penalty": 1.0,
        "num_ctx": 2048
      }
    }
  }
]
```


### Пример ответов (stream)

### Event 1
```json
{
    "id": 1,
    "payload": {
        "id": "c7fd21f6f3614803b8d8f3679d60f14d",
        "object": "chat.completion",
        "created": 1776841152,
        "model": "qwen3:14b",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Вот реализация функции проверки палиндрома с использованием оптимального алгоритма:\n\n```python\ndef is_palindrome(s: str) -> bool:\n    \"\"\"\n    Проверяет, является ли строка палиндромом.\n    \n    Использует двух указателей для сравнения символов с начала и конца строки.\n    Время выполнения: O(n), Память: O(1)\n    \n    Args:\n        s: Входная строка.\n        \n    Returns:\n        True, если строка является палиндромом, иначе False.\n    \"\"\"\n    i, j = 0, len(s) - 1\n    while i < j:\n        if s[i] != s[j]:\n            return False\n        i += 1\n        j -= 1\n    return True\n```\n\n### Объяснение решения:\n\n1. **Алгоритм двух указателей**:\n   - Мы используем два указателя: `i` (начало строки) и `j` (конец строки).\n   - В цикле сравниваем символы на позициях `i` и `j`.\n   - Если символы не совпадают, возвращаем `False`.\n   - Если совпадают, сдвигаем указатели: `i` вперёд, `j` назад.\n   - Если цикл завершён без возврата `False`, строка является палиндромом, возвращаем `True`.\n\n2. **Оптимальность**:\n   - **Время выполнения**: O(n), где n — длина строки. Мы проходим по строке один раз.\n   - **Память**: O(1), так как не создаём новых строк и используем только переменные для указателей.\n\n3. **Примеры использования**:\n   ```python\n   print(is_palindrome(\"radar\"))      # True\n   print(is_palindrome(\"hello\"))      # False\n   print(is_palindrome(\"abba\"))       # True\n   print(is_palindrome(\"\"))           # True (пустая строка считается палиндромом)\n   print(is_palindrome(\"A man a plan a canal Panama\"))  # False (без предварительной обработки)\n   ```\n\n### Дополнительные замечания:\n- Если требуется игнорировать регистр, пробелы и знаки препинания, нужно предварительно обработать строку (например, удалить неалфавитные символы и привести к нижнему регистру). В текущей реализации это не делается, так как условие задачи не требует этого."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        },
        "thread_id": "c7fd21f6f3614803b8d8f3679d60f14d",
        "conversation_id": "c7fd21f6f3614803b8d8f3679d60f14d"
    }
}
```

### Event 2
```json
{
    "id": 2,
    "payload": {
        "id": "87e34f048ab5428ab7bb64280cf04303",
        "object": "chat.completion",
        "created": 1776841195,
        "model": "qwen3:14b",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Для проверки, является ли строка палиндромом, можно использовать следующий эффективный алгоритм, который работает в **O(n)** времени и **O(1)** памяти, используя **два указателя**:\n\n### Реализация:\n```python\ndef is_palindrome(s):\n    left = 0\n    right = len(s) - 1\n\n    while left < right:\n        if s[left] != s[right]:\n            return False\n        left += 1\n        right -= 1\n\n    return True\n```\n\n---\n\n### Объяснение:\n\n1. **Инициализация указателей**:\n   - Указатель `left` начинает с начала строки.\n   - Указатель `right` начинает с конца строки.\n\n2. **Сравнение символов**:\n   - В цикле, пока `left < right`, сравниваются символы на позициях `left` и `right`.\n   - Если символы не совпадают, функция возвращает `False`.\n\n3. **Завершение цикла**:\n   - Если все символы совпали, функция возвращает `True`.\n\n---\n\n### Примеры:\n\n```python\nprint(is_palindrome(\"madam\"))      # True\nprint(is_palindrome(\"hello\"))      # False\nprint(is_palindrome(\"a\"))          # True\nprint(is_palindrome(\"\"))           # True\n```\n\n---\n\n### Преимущества алгоритма:\n\n- **Эффективность по памяти**: Не создаёт новых объектов (в отличие от использования срезов).\n- **Линейная сложность**: Операции выполняются за время, пропорциональное длине строки.\n- **Простота реализации**: Логика понятна и легко читается.\n\n---\n\n### Примечание:\n\nЕсли требуется игнорировать регистр и символы (например, пробелы), можно предварительно обработать строку. Но в текущем задании это не требуется, и реализация описана для случая, когда строка состоит из символов, которые нужно сравнить напрямую."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        },
        "thread_id": "87e34f048ab5428ab7bb64280cf04303",
        "conversation_id": "87e34f048ab5428ab7bb64280cf04303"
    }
}
```

### Event 3
```json
{
    "id": 3,
    "payload": {
        "id": "b2e1aafceaa24589be4c92bd3a8daa43",
        "object": "chat.completion",
        "created": 1776841349,
        "model": "qwen3:14b",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Чтобы проверить, является ли строка палиндромом, игнорируя неалфавитно-цифровые символы и регистр, следует выполнить следующие шаги:\n\n### **1. Предварительная обработка строки**\n- **Удалите все неалфавитно-цифровые символы** (например, пробелы, запятые, двоеточия).\n- **Приведите строку к одному регистру** (например, все символы в нижний регистр).\n\nПример:\n```python\nimport re\n\ndef preprocess(s):\n    return re.sub(r'[^a-zA-Z0-9]', '', s).lower()\n```\n\n### **2. Проверка на палиндром с использованием двух указателей**\n- Используйте два указателя: `left` (начало строки) и `right` (конец строки).\n- Сравнивайте символы, двигаясь к центру строки. Если символы не совпадают, строка не является палиндромом.\n\nПример:\n```python\ndef is_palindrome(s):\n    s = preprocess(s)\n    left, right = 0, len(s) - 1\n    while left < right:\n        if s[left] != s[right]:\n            return False\n        left += 1\n        right -= 1\n    return True\n```\n\n### **Пример работы**\nДля строки `\"A man, a plan, a canal: Panama\"`:\n1. После предварительной обработки: `\"amanaplanacanalpanama\"`.\n2. Указатели сравнивают символы с обоих концов, двигаясь к центру. Все символы совпадают, поэтому строка является палиндромом.\n\n### **Важные моменты**\n- **Предварительная обработка** упрощает логику проверки, так как избавляет от необходимости обрабатывать неалфавитно-цифровые символы в процессе сравнения.\n- **Регистр** игнорируется за счёт приведения строки к нижнему регистру.\n\n### **Альтернативный подход (без предварительной обработки)**\nЕсли вы хотите избежать создания новой строки, можно обработать символы в процессе сравнения:\n```python\ndef is_palindrome(s):\n    left, right = 0, len(s) - 1\n    while left < right:\n        # Пропуск неалфавитно-цифровых символов\n        while left < right and not s[left].isalnum():\n            left += 1\n        while left < right and not s[right].isalnum():\n            right -= 1\n        # Сравнение символов (игнорируя регистр)\n        if s[left].lower() != s[right].lower():\n            return False\n        left += 1\n        right -= 1\n    return True\n```\n\n### **Итог**\nОба подхода корректно проверяют, является ли строка палиндромом. Первый (с предварительной обработкой) более читабелен, второй — экономичнее по памяти. Выбор зависит от конкретных требований."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        },
        "thread_id": "b2e1aafceaa24589be4c92bd3a8daa43",
        "conversation_id": "b2e1aafceaa24589be4c92bd3a8daa43"
    }
}
```

### Event 4 (стрим завершён)
```
[DONE]
```