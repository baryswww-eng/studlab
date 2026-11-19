# STUD LAB

**Learn. Practice. Build.** · Учись. Практикуйся. Развивайся.

Онлайн-платформа (LMS) для изучения IT и программирования на русском языке. **Все курсы бесплатные.** Каждый курс: теория → видеоуроки → тесты и практические задания с AI-проверкой. Плюс личный кабинет с прогрессом и AI-ассистент на Google Gemini, который отвечает на любые вопросы.

| Часть | Технологии |
|---|---|
| Frontend | Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS 4, компоненты в стиле shadcn/ui, next-intl, React Hook Form, Zod, react-markdown |
| Backend | Python 3.12, FastAPI, Pydantic 2, SQLAlchemy 2.1 (async), Alembic, asyncpg, argon2-cffi, PyJWT, httpx |
| Данные и сервисы | PostgreSQL, Google Gemini API, YouTube (встраивание видео) |
| Инфраструктура | Docker Compose (описан), локальный PostgreSQL без Docker (`scripts/dev-db.ps1`) |

## Что готово

| Функция | Статус |
|---|---|
| Главная: hero, рекомендуемые курсы, направления, преимущества, шаги обучения, **реальная** статистика из БД, демо-отзывы (помечены «Demo») | ✅ |
| Каталог `/courses`: поиск, фильтры по направлению / уровню / цене, сортировка, пагинация (всё в URL) | ✅ |
| Страница курса: описание, результаты, требования, преподаватель и **содержание в 3 разделах**: 1) Теория, 2) Видеоуроки, 3) Тесты и практические задания | ✅ |
| **Теория**: по 3 статьи на курс (24 статьи) с примерами кода и таблицами, отдельно для каждого курса | ✅ `backend/app/scripts/demo_content.py` |
| **Тесты** с автопроверкой: один / несколько вариантов / ввод ответа, зачёт от 70 %, разбор с объяснениями; правильные ответы не отправляются в браузер до сдачи | ✅ 8 тестов по 6 вопросов |
| **Практические задания** (16): решение проверяет STUD AI по скрытым критериям преподавателя — балл 0–100, статус «Принято / Нужно доработать», отзыв; если AI недоступен — «Ожидает проверки» | ✅ |
| **55 видеоуроков YouTube на русском** — смотреть можно **без записи и без входа** | ✅ плеер `youtube-nocookie.com`, указан автор канала и ссылка на YouTube |
| **Регистрация и вход** по email и паролю, выход | ✅ |
| **Личный кабинет**: `/dashboard` (статистика, «Продолжить обучение»), `/my-courses`, `/profile`, `/settings` | ✅ |
| **Прогресс**: «Отметить урок пройденным», галочки и процент в содержании курса; курс сам попадает в «Мои курсы» | ✅ |
| **STUD AI** (Google Gemini) — как ChatGPT: отвечает на **любые** вопросы на языке вопроса, ответ печатается потоком, кнопка «Остановить»; режимы «Свободный чат», «Объяснить тему», «Разобрать код», «Тест по теме», «Практика»; чат на каждом уроке с контекстом урока | ✅ работает с настоящим Gemini |
| О платформе, политика конфиденциальности, условия использования, страница состояния системы `/status` | ✅ юридические тексты — **черновик**, нужна проверка юристом |
| Адаптивная вёрстка (desktop / tablet / mobile), тёмная тема Dark Premium, доступность (label, aria, клавиатура) | ✅ |

### Не сделано (сознательно отложено)

- Проверка заданий преподавателем вручную (сейчас проверяет только AI; задания без AI-отзыва ждут проверки).
- Сертификаты, геймификация (XP, достижения, рейтинг), отзывы и рейтинг курсов.
- Кабинеты преподавателя и администратора (роли и проверка `require_role` на backend уже есть).
- Вход через Google и восстановление пароля по email (нужны OAuth и почтовый сервис).
- Встроенный редактор и запуск кода (по ТЗ — только в изолированной песочнице).
- Docker Compose описан, но **не проверен**: Docker на машине разработки не установлен.

**Демо-данные:** 8 курсов и 3 преподавателя помечены `is_demo=true` (бейдж «Demo»), демо-преподаватели войти не могут. Видео принадлежат их авторам на YouTube и встроены в учебных целях; список — `backend/app/scripts/demo_videos.py`.

## Запуск (Windows, без Docker)

### 1. Настройки

```powershell
Copy-Item .env.example .env
```

В `.env` задайте `POSTGRES_PASSWORD`, `DATABASE_URL`, `SECRET_KEY` и (для AI) `GEMINI_API_KEY`. Сгенерировать `SECRET_KEY`:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

### 2. База данных (внутри проекта, без прав администратора)

`scripts/dev-db.ps1` кладёт PostgreSQL 16 (pip-пакет `pgserver`) в `.local/pg`, данные — в `.local/pgdata`, создаёт базы `studlab` и `studlab_test` и слушает только `127.0.0.1:5432`.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/dev-db.ps1 start
```

Остановить / статус: `dev-db.ps1 stop`, `dev-db.ps1 status`. После перезагрузки компьютера снова выполните `start`. Проект лежит в OneDrive — если синхронизация мешает базе, исключите папку `.local`.

### 3. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m app.scripts.seed_demo
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

`seed_demo` можно запускать повторно; `--reset` пересоздаёт демо-данные. Swagger: http://localhost:8000/docs

### 4. Frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env.local
npm run dev
```

Сайт: http://localhost:3000

### С Docker (когда он будет установлен)

```powershell
docker compose up --build
```

Backend-контейнер сам выполняет `alembic upgrade head`; демо-данные — `docker compose exec backend python -m app.scripts.seed_demo`.

## Проверки

```powershell
cd backend; .\.venv\Scripts\python.exe -m pytest -q; .\.venv\Scripts\python.exe -m ruff check .
```

```powershell
cd frontend; npx tsc --noEmit; npm run lint; npm run build
```

Интеграционные тесты используют только базу `TEST_DATABASE_URL` (`studlab_test`); без неё они пропускаются. Реальный Gemini в тестах не вызывается (подменён `httpx.MockTransport`).

## Авторизация

- `POST /api/v1/auth/register`, `POST /api/v1/auth/login` → backend ставит HttpOnly-cookie `studlab_session` (JWT HS256 на `SECRET_KEY`, 7 дней, `SameSite=Lax`, `Secure` в продакшене).
- Пароли — только хеш **Argon2id**; правило: 8–128 символов, буквы и цифры. Email в нижнем регистре, дубликат → 409.
- Неверный пароль и несуществующий email отвечают одинаково и за одинаковое время.
- Защита от подбора: 10 попыток входа за 15 минут (IP + email), 5 регистраций в час с IP → 429 с `Retry-After`.
- Заблокированный пользователь (`is_active=false`) теряет и вход, и текущую сессию.

## AI-преподаватель (Google Gemini)

1. Ключ: https://aistudio.google.com/apikey → в `.env`: `GEMINI_API_KEY=...`.
2. Перезапустите backend; проверка: `GET /api/v1/ai/status` → `"enabled": true`.

- Все запросы идут через backend; ключ уходит в Gemini в заголовке `x-goog-api-key` и **никогда не попадает в браузер**.
- Модель `GEMINI_MODEL` (по умолчанию `gemini-3.1-flash-lite` — самая быстрая для этого ключа), запасные — `GEMINI_FALLBACK_MODELS`. **Страховочные запросы:** если модель молчит 6 с, параллельно запускается следующая, берётся первый ответ; таймаут одной модели — `AI_TIMEOUT_SECONDS` (45 с). Доступные ключу модели: `python -m app.ai.list_models`.
- Лимиты: без входа — 10 вопросов в час с IP; после входа — 30 в час и 100 в день. История диалогов вошедших пользователей и токены сохраняются (`ai_conversations`, `ai_messages`).
- На странице урока в запрос добавляется контекст (курс, модуль, урок). Ответы рендерятся без сырого HTML (защита от XSS).

## API

| Endpoint | Описание |
|---|---|
| `GET /api/v1/health`, `GET /api/v1/health/db` | состояние API и базы |
| `GET /api/v1/categories`, `GET /api/v1/courses?q&category&level&price&sort&page` | каталог |
| `GET /api/v1/courses/{slug}` | курс с программой |
| `GET /api/v1/lessons/{id}` | урок с видео — **публично** |
| `GET /api/v1/stats/public` | реальные счётчики |
| `POST /api/v1/auth/register`, `/login`, `/logout` | авторизация |
| `GET`, `PATCH /api/v1/users/me` | текущий пользователь |
| `GET /api/v1/users/me/dashboard`, `POST /api/v1/users/me/password` | кабинет; смена пароля |
| `PUT`, `DELETE /api/v1/progress/lessons/{id}`, `GET /api/v1/progress/courses/{slug}` | прогресс |
| `GET /api/v1/ai/status`, `POST /api/v1/ai/chat`, `POST /api/v1/ai/chat/stream` (SSE) | AI-ассистент |
| `GET /api/v1/quizzes/by-lesson/{id}`, `POST /api/v1/quizzes/{id}/submit` | тест (сдача отмечает урок пройденным) |
| `GET /api/v1/assignments/by-lesson/{id}`, `POST /api/v1/assignments/{id}/submissions` | задание + AI-проверка (20 отправок в сутки) |

Ошибки всегда в формате `{"error": {"code", "message"}}` без внутренних деталей.

## Структура

```text
STUD-LAB/
├── frontend/src/
│   ├── app/[locale]/        страницы (единственная локаль ru, URL без префикса)
│   │   └── (cabinet)/       dashboard, my-courses, profile, settings
│   ├── components/          ui/ и layout/ (шапка, подвал, навигация)
│   ├── features/            auth, ai, cabinet, courses, lessons, progress, landing, legal, system-status
│   ├── i18n/, locales/      next-intl и все тексты (ru.json)
│   ├── lib/, services/      API-клиент и запросы к backend
│   └── types/
├── backend/
│   ├── app/
│   │   ├── api/v1/          endpoints: health, catalog, auth, users, progress, ai
│   │   ├── ai/              клиент Gemini, промпты, сервис
│   │   ├── core/            настройки, ошибки, пароли, сессии, лимиты
│   │   ├── database/        Base, async engine
│   │   ├── models/          users, roles, courses, modules, lessons, progress, ai
│   │   ├── repositories/, services/, schemas/
│   │   └── scripts/         seed_demo, demo_videos
│   ├── migrations/          Alembic
│   └── tests/               pytest (88 тестов)
├── scripts/dev-db.ps1       локальный PostgreSQL
├── docs/architecture.md
├── docker-compose.yml
└── .env.example
```

## Безопасность

- `.env` и `.local/` не попадают в Git; в `.env.example` нет настоящих ключей.
- `GEMINI_API_KEY` есть только на backend.
- При `ENVIRONMENT=production` слабый `SECRET_KEY` и `CORS_ORIGINS=*` не принимаются, cookie становится `Secure`, `/docs` отключается.
- CORS — только явные домены; все права проверяются на backend.
