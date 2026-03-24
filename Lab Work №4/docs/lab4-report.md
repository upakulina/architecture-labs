# Лабораторная работа №4
**Тема:** Проектирование REST API
**Цель работы:** Получить опыт проектирования программного интерфейса.

## Принятые проектные решения
### Контекст и выбранный сервис
Выбранный сервис системы: Gradebook Service (сервис рабочих ведомостей). Он отвечает за ведение ведомостей по дисциплинам/группам, элементы контроля, оценки, посещаемость и формирование итогов.

Базовый URL API (пример): `/api/v1`

### Решение 1. Версионирование API через URL
Решение: использовать версию в URL: `/api/v1/....`

Версионирование позволяет безопасно развивать API и в будущем вводить несовместимые изменения через `/api/v2/...` без поломки клиентов.
### Решение 2. Ресурсный подход и нейминг в множественном числе
Решение: все сущности представлены как ресурсы, пути — существительные во множественном числе, например:
- `/gradebooks`
- `/gradebooks/{gradebookId}/assessment-items`
- `/gradebooks/{gradebookId}/grades`

Это соответствует REST-стилю: URI описывает ресурс, а действие задаётся HTTP-методом.

### Решение 3. Использование HTTP-методов по назначению (GET/POST/PUT/DELETE)
Решение:
- `GET` — получение данных (идемпотентно)
- `POST` — создание ресурса или выполнение серверной операции, приводящей к созданию/изменению состояния (не идемпотентно)
- `PUT` — полная замена/обновление ресурса (идемпотентно)
- `DELETE` — удаление ресурса (идемпотентно)
  
Корректное использование методов упрощает понимание, кэширование и тестирование API.

### Решение 4. Идентификаторы ресурсов — UUID
Решение: все основные сущности (gradebook, assessment item, grade, attendance record) идентифицируются UUID.

UUID удобны для распределённых систем, позволяют создавать сущности без зависимости от последовательных автоинкрементов и проще при интеграциях.

### Решение 5. Стандартизированные коды ответов и единый формат ошибок
Успешные ответы:
- `200 OK` — успешный GET/PUT/DELETE.
- `201 Created` — успешный POST создания ресурса (с Location).
- `204 No Content` — успешный DELETE без тела ответа (или PUT, если не возвращаем тело).

Ошибки:
- `400 Bad Request` — некорректный запрос/валидация.
- `401 Unauthorized` — не аутентифицирован.
- `403 Forbidden` — нет прав.
- `404 Not Found` — ресурс не найден.
- `409 Conflict` — конфликт состояния (например, попытка редактировать закрытую ведомость).
- `422 Unprocessable Entity` — семантическая ошибка (например, points > maxPoints).
- `500 Internal Server Error` — непредвиденная ошибка.

Формат ошибки (единый JSON):
``` 
{
  "error": {
    "code": "GRADEBOOK_CLOSED",
    "message": "Gradebook is closed and cannot be modified.",
    "details": { "gradebookId": "..." },
    "traceId": "..." 
  }
}
```
Единый формат облегчает обработку ошибок на фронте и в тестах, коды — стандартный контракт взаимодействия.

## Документация по API

**Base URL:** `/api/v1`

**Content-Type:** application/json

**Формат дат/времени:** ISO 8601 в UTC

### 1) Получить список ведомостей
**Метод:** `GET`

**URL:** `/api/v1/gradebooks`

**Query-параметры:**
- `status` — DRAFT | OPEN | CLOSED
- `semester` — строка, например 2025S
- `groupId` — UUID
- `disciplineId` — UUID
- `limit` — число (по умолчанию 20)
- `offset` — число (по умолчанию 0)
- `sort` — строка, например -createdAt или createdAt

**Пример запроса:**
`GET /api/v1/gradebooks?status=OPEN&semester=2025S&limit=20&offset=0&sort=-createdAt`

**Ответ 200 (JSON):**
```
{
  "items": [
    {
      "id": "c0f2b0c9-2f9d-44de-9b1e-2b08d2e6f6a6",
      "discipline": { "id": "1b2c3d4e-1111-2222-3333-444455556666", "name": "Базы данных" },
      "group": { "id": "9a8b7c6d-aaaa-bbbb-cccc-ddddeeeeffff", "name": "РИС-22-3" },
      "semester": "2025S",
      "status": "OPEN",
      "createdAt": "2026-02-22T12:30:00Z"
    }
  ],
  "paging": { "limit": 20, "offset": 0, "total": 1 }
}
```
### 2) Создать ведомость
**Метод:** `POST`

**URL:** `/api/v1/gradebooks`

**Тело запроса (JSON):**
```
{
  "disciplineId": "1b2c3d4e-1111-2222-3333-444455556666",
  "groupId": "9a8b7c6d-aaaa-bbbb-cccc-ddddeeeeffff",
  "semester": "2025S"
}
```
**Ответ 201 (JSON + Location):**

Header: `Location: /api/v1/gradebooks/{gradebookId}`
```
{
  "id": "c0f2b0c9-2f9d-44de-9b1e-2b08d2e6f6a6",
  "discipline": { "id": "1b2c3d4e-1111-2222-3333-444455556666", "name": "Базы данных" },
  "group": { "id": "9a8b7c6d-aaaa-bbbb-cccc-ddddeeeeffff", "name": "РИС-22-3" },
  "semester": "2025S",
  "status": "DRAFT",
  "createdAt": "2026-02-22T12:30:00Z"
}
```
**Ошибки:**
- `400` — отсутствуют обязательные поля
- `409` — ведомость для этой дисциплины/группы/семестра уже существует

### 3) Получить ведомость по id
**Метод:** `GET`

**URL:** `/api/v1/gradebooks/{gradebookId}`

**Path-параметр:** `gradebookId` — UUID

**Query-параметры:**
- `includeItems` — `true | false` — включать ли элементы контроля в ответ
- `includeGrades` — `true | false` — включать ли оценки студентов
- `includeAttendance` — `true | false` — включать ли данные по посещаемости
- `includeStats` — `true | false` — включать ли агрегированную статистику по ведомости

**Ответ 200 (JSON):**
```
{
  "id": "c0f2b0c9-2f9d-44de-9b1e-2b08d2e6f6a6",
  "discipline": { "id": "1b2c3d4e-1111-2222-3333-444455556666", "name": "Базы данных" },
  "group": { "id": "9a8b7c6d-aaaa-bbbb-cccc-ddddeeeeffff", "name": "РИС-22-3" },
  "semester": "2025S",
  "status": "OPEN",
  "createdAt": "2026-02-22T12:30:00Z"
}
```
**Ошибки:**
- `404` — ведомость не найдена

### 4) Получить элементы контроля ведомости

**Метод:** `GET`

**URL:** `/api/v1/gradebooks/{gradebookId}/assessment-items`

**Path-параметры:** `gradebookId` — UUID

**Query-параметры:**

- `title` — фильтр по названию элемента контроля
- `sort` — строка, например title, -title, weight, -weight
- `limit` — ограничение количества записей
- `offset` — смещение для пагинации

**Ответ 200 (JSON):**
```
{
  "items": [
    {
      "id": "b1111111-2222-3333-4444-555555555555",
      "title": "Лабораторная №1",
      "maxPoints": 10,
      "weight": 0.1
    }
  ]
}
```
### 5) Добавить элемент контроля в ведомость

**Метод:** `POST`

**URL:** `/api/v1/gradebooks/{gradebookId}/assessment-items`

**Тело запроса (JSON):**
```
{
  "title": "Лабораторная №1",
  "maxPoints": 10,
  "weight": 0.1
}
```

**Ответ 201 (JSON + Location):**

**Header:** `Location: /api/v1/gradebooks/{gradebookId}/assessment-items/{itemId}`
```
{
  "id": "b1111111-2222-3333-4444-555555555555",
  "title": "Лабораторная №1",
  "maxPoints": 10,
  "weight": 0.1
}
```
**Ошибки:**
- `409` — нельзя менять элементы контроля, если ведомость закрыта (status=CLOSED)
- `422` — неверные значения (например, maxPoints <= 0, weight < 0)

### 6) Получить оценки по ведомости (с фильтром по студенту)

**Метод:** `GET`

**URL:** `/api/v1/gradebooks/{gradebookId}/grades`

**Query-параметры:**
- `studentId` — UUID — фильтр по студенту
- `assessmentItemId` — UUID — фильтр по конкретному элементу контроля
- `updatedAfter` — дата/время в ISO 8601 — вернуть только оценки, изменённые после указанного момента
- `limit` — ограничение количества записей
- `offset` — смещение для пагинации
- `sort` — строка, например updatedAt, -updatedAt, points, -points

**Пример:** `GET /api/v1/gradebooks/{gradebookId}/grades?studentId=57586896`

**Ответ 200 (JSON):**
```
{
  "gradebookId": "54567",
  "studentId": "57586896",
  "items": [
    {
      "assessmentItemId": "11111111",
      "points": 8,
      "updatedAt": "2026-02-22T12:40:00Z"
    }
  ],
  "total": 8,
  "status": "AtRisk"
}
```
### 7) Добавить/обновить оценку 

**Метод:** `POST`

**URL:** `/api/v1/gradebooks/{gradebookId}/grades`

**Тело запроса (JSON):**
```
{
  "studentId": "43778781",
  "assessmentItemId": "28743879",
  "points": 8
}
```
**Ответ 200 (JSON):**
```
{
  "gradebookId": "876567",
  "studentId": "586857",
  "total": 8,
  "status": "AtRisk",
  "updatedAt": "2026-02-22T12:40:00Z"
}
```
**Ошибки:**
- `409` — ведомость закрыта, редактирование запрещено
- `422` — points выходит за допустимый диапазон (0..maxPoints)

### 8) Запустить формирование отчёта по ведомости

**Метод:** `POST`

**URL:** `/api/v1/gradebooks/{gradebookId}/reports`

**Тело запроса (JSON):**
```
{
  "format": "XLSX"
}
```
**Ответ 202 (JSON):**
```
{
  "reportId": "768697",
  "status": "QUEUED"
}
```
Отчёт формируется асинхронно, поэтому возвращаем 202 Accepted и reportId.

### 9) Обновить элемент контроля (редактирование Assessment Item)
**Метод:** `PUT`

**URL:** `/api/v1/gradebooks/{gradebookId}/assessment-items/{itemId}`

**Path-параметры:**
- `gradebookId` — UUID
- `itemId` — UUID

**Пример запроса:**
`PUT /api/v1/gradebooks/482057/assessment-items/438578`

**Тело запроса (JSON):**
```
{
  "title": "Лабораторная №1 (обновлено)",
  "maxPoints": 12,
  "weight": 0.15
}
```
**Ответ 200 (JSON):**
```
{
  "id": "b1111111-2222-3333-4444-555555555555",
  "title": "Лабораторная №1 (обновлено)",
  "maxPoints": 12,
  "weight": 0.15
}
```
**Ошибки:**
- `404` — ведомость или элемент контроля не найден
- `409` — ведомость закрыта (status=CLOSED), редактирование запрещено
- `422` — некорректные значения (maxPoints <= 0, weight < 0 и т.п.)

### 10) Удалить элемент контроля из ведомости
**Метод:** `DELETE`

**URL:** `/api/v1/gradebooks/{gradebookId}/assessment-items/{itemId}`

**Path-параметры:**
- `gradebookId` — UUID
- `itemId` — UUID

**Пример запроса:**
`DELETE /api/v1/gradebooks/32789456/assessment-items/8327589`

**Ответ 204 (No Content):** тело ответа отсутствует

**Ошибки:**
- `404` — ведомость или элемент контроля не найден
- `409` — ведомость закрыта (status=CLOSED), удаление запрещено
- `409` — есть оценки, привязанные к этому itemId (конфликт целостности данных)
(в этом случае можно требовать сначала удалить/обнулить оценки, либо делать “soft delete”)

**Пример ошибки 409 (JSON):**
```
{
  "error": {
    "code": "ASSESSMENT_ITEM_HAS_GRADES",
    "message": "Cannot delete assessment item because grades exist.",
    "details": {
      "gradebookId": "c0f2b0c9-2f9d-44de-9b1e-2b08d2e6f6a6",
      "itemId": "b1111111-2222-3333-4444-555555555555"
    },
    "traceId": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
  }
}
```

## Тестирование API
<
По каждому реализуемому API предоставить следующую информацию: 
Тестируемое API.
Метод.
Строка запроса, используемая для тестирования. Можно представить в виде текстовой строки или принтскрина из Postman, чтобы продемонстрировать все передаваемые данные.
Принтскрин из Postman передаваемых заголовков и параметров (Params, Authorization, Headers, Body).
Принтскрины из Postman полученного ответа (Body и Headers).
Код автотестов (на получение возвращаемого статуса и содержимого ответа).
Принтскрины из Postman результатов тестирования (Test Results).
>
