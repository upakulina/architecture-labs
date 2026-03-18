# Лабораторная работа №5
**Тема:** Реализация архитектуры на основе сервисов (микросервисной архитектуры)

**Цель работы:** Получить опыт работы организации взаимодействия сервисов с использованием контейнеров Docker

# Реализация контейнеров
## Реализованная архитектура

В рамках лабораторной работы реализовано приложение, состоящее из трех взаимодействующих контейнеров:

1. `frontend` — клиентская часть;
2. `backend` — серверная часть с REST API;
3. `db` — база данных PostgreSQL.

Контейнеры запускаются через `docker compose` и взаимодействуют друг с другом по внутренней сети Docker.

Общая схема взаимодействия:

`frontend → backend → db`

## Состав контейнеров

### 1. Frontend

Контейнер `frontend` построен на базе `nginx`.

Он отдает пользовательский интерфейс системы рабочих ведомостей и проксирует запросы к серверной части.

Через интерфейс доступны следующие действия:
- получение списка ведомостей;
- добавление оценки в ведомость.

### 2. Backend

Контейнер `backend` реализован на FastAPI.

Реализованные endpoint’ы:
- `GET /health`
- `GET /api/v1/gradebooks`
- `GET /api/v1/gradebooks/{gradebook_id}`
- `POST /api/v1/gradebooks/{gradebook_id}/grades`

Backend обрабатывает запросы клиентской части и выполняет операции с базой данных.

### 3. Database

Контейнер `db` использует PostgreSQL.

Для инициализации БД используется файл `init.sql`, который:
- создает таблицы `gradebooks` и `grades`;
- заполняет их тестовыми данными.

## Файлы проекта

Структура проекта:

```text
LabWork5/
  docs/
    lab5-report.md
    images/
      lab5-containers.png
      lab5-health.png
      lab5-swagger.png
      lab5-frontend.png
      lab5-frontend-actions.png
      lab5-actions-success.png
      lab5-newman.png
  src/
    backend/
      Dockerfile
      requirements.txt
      app/
        main.py
    frontend/
      Dockerfile
      nginx.conf
      index.html
      app.js
    db/
      init.sql
  postman/
    lab5_collection.json

.github/
  workflows/
    ci.yml

docker-compose.yml
.gitignore
```

## Локальный запуск приложения

### Команда запуска

```bash
docker compose up --build
```

После запуска приложение доступно по адресам:
- Frontend: `http://localhost:8080`
- Backend health: `http://localhost:8000/health`
- Swagger UI: `http://localhost:8000/docs`

### Результат запуска

После выполнения команды были успешно созданы и запущены контейнеры:
- `gradebook_frontend`
- `gradebook_backend`
- `gradebook_db`

![Рисунок 1 — Состояние контейнеров после запуска](images/lab5-containers.png)

## Проверка работоспособности

### Проверка backend

Для проверки доступности backend использовался запрос:

```bash
curl http://localhost:8000/health
```

Ожидаемый результат:

```json
{"status":"ok"}
```

![Рисунок 2 — Проверка доступности backend](images/lab5-health.png)

### Проверка Swagger UI

Swagger-документация backend доступна по адресу:

`http://localhost:8000/docs`

![Рисунок 3 — Swagger UI реализованного API](images/lab5-swagger.png)

### Проверка frontend

После открытия страницы `http://localhost:8080` через интерфейс были успешно выполнены действия:
- получение списка ведомостей;
- добавление новой оценки в ведомость.

![Рисунок 4 — Клиентская часть системы](images/lab5-frontend.png)

![Рисунок 5 — Получение списка ведомостей и добавление оценки](images/lab5-frontend-actions.png)

## Непрерывная интеграция (CI)

В проекте настроен GitHub Actions workflow, который выполняет:
1. получение исходного кода из репозитория;
2. сборку Docker-образов;
3. запуск контейнеров через `docker compose`;
4. ожидание готовности backend;
5. запуск интеграционных тестов;
6. остановку контейнеров после завершения.

Файл workflow:

```text
.github/workflows/ci.yml
```

Основные шаги workflow:
- `Checkout repository`
- `Show Docker versions`
- `Build Docker images`
- `Start containers`
- `Wait for backend health`
- `Setup Node.js`
- `Install Newman`
- `Run Postman integration tests`
- `Show container status`
- `Stop containers`

![Рисунок 6 — Успешное выполнение GitHub Actions workflow](images/lab5-actions-success.png)

## 7. Интеграционные тесты

Интеграционные тесты реализованы в виде Postman-коллекции:

```text
LabWork5/postman/lab5_collection.json
```

В коллекции тестируются следующие сценарии:
- `GET /health`
- `GET /api/v1/gradebooks`
- `GET /api/v1/gradebooks/1`
- `POST /api/v1/gradebooks/1/grades`

Тесты запускаются автоматически в CI с помощью Newman.

Пример команды запуска:

```bash
newman run LabWork5/postman/lab5_collection.json --env-var baseUrl=http://localhost:8000
```

![Рисунок 7 — Успешный запуск Postman/Newman тестов в CI](images/lab5-newman.png)
