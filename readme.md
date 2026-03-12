# Grok2API

**Русский** | [中文](docs/README.cn.md) | [English](docs/README.en.md)

> [!NOTE]
> Этот проект предназначен исключительно для обучения и исследований. Пользователи обязаны соблюдать **условия использования** Grok и действующее **законодательство**. Запрещено использовать в незаконных целях.

> [!NOTE]
> Форк проекта [chenyme/grok2api](https://github.com/chenyme/grok2api). Оригинальный автор — [@chenyme](https://github.com/chenyme). Ни на что не претендую и все такое.

Grok2API на базе **FastAPI** — полная совместимость с форматом вызовов OpenAI API. Поддерживает потоковые/непотоковые диалоги, вызов инструментов (tool calling), генерацию/редактирование изображений, генерацию видео, глубокое мышление (thinking), пул токенов с автоматической балансировкой нагрузки.

---

## Быстрый старт

### Локальная разработка

```bash
uv sync

uv run granian --interface asgi --host 0.0.0.0 --port 8000 --workers 1 main:app
```

### Docker Compose

```bash
git clone https://github.com/niemandswasser/grok2api
cd grok2api
docker compose up -d
```

> **Порты Docker Compose:**
>
> - `SERVER_PORT` — порт внутри контейнера
> - `HOST_PORT` — порт на хост-машине (только для Docker Compose)
>
> Правило маппинга: `HOST_PORT:SERVER_PORT`. Вы обращаетесь к `HOST_PORT`, а сервис внутри контейнера слушает `SERVER_PORT`.
>
> Пример: `HOST_PORT=9000 SERVER_PORT=8011 docker compose up -d` → доступ по `http://localhost:9000`.

### Деплой на Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/chenyme/grok2api&env=LOG_LEVEL,LOG_FILE_ENABLED,DATA_DIR,SERVER_STORAGE_TYPE,SERVER_STORAGE_URL&envDefaults=%7B%22DATA_DIR%22%3A%22/tmp/data%22%2C%22LOG_FILE_ENABLED%22%3A%22false%22%2C%22LOG_LEVEL%22%3A%22INFO%22%2C%22SERVER_STORAGE_TYPE%22%3A%22local%22%2C%22SERVER_STORAGE_URL%22%3A%22%22%7D)

> Обязательно задайте `DATA_DIR=/tmp/data` и отключите файловые логи `LOG_FILE_ENABLED=false`.
>
> Для персистентности используйте MySQL / Redis / PostgreSQL: задайте `SERVER_STORAGE_TYPE` и `SERVER_STORAGE_URL`.

### Деплой на Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/chenyme/grok2api)

> Бесплатные инстансы Render засыпают через 15 минут без обращений; при перезапуске данные теряются.
>
> Для персистентности используйте MySQL / Redis / PostgreSQL: задайте `SERVER_STORAGE_TYPE` и `SERVER_STORAGE_URL`.

---

## Панель управления

- Адрес: `http://<host>:<port>/admin` (локально — `SERVER_PORT`, Docker Compose — `HOST_PORT`, по умолчанию `8000`)
- Пароль по умолчанию: `grok2api` (параметр `app.app_key`, рекомендуется изменить)

**Возможности:**

- **Управление токенами** — импорт, добавление, удаление токенов; просмотр статуса и квот
- **Фильтрация по статусу** — активные / ограниченные / недействительные / NSFW статус
- **Массовые операции** — обновление, экспорт, удаление, включение NSFW
- **Включение NSFW** — одной кнопкой активировать режим Unhinged (требуется прокси или `cf_clearance`)
- **Управление конфигурацией** — онлайн-редактирование системных настроек
- **Управление кэшем** — просмотр и очистка медиа-кэша

---
### Генерация изображений

Для инлайн-генерации изображений в ST рекомендуется расширение [sillyimages](https://github.com/niemandswasser/sillyimages-grr)) с поддержкой режима **Grok** — отправляет референсные изображения (аватарки персонажей) вместе с промптом через `/v1/chat/completions`. Также работает поддержка генерации через ссылку.

Настройки расширения:
- Тип API: **Grok (grok2api — рефы через chat)**
- URL эндпоинта: `http://localhost:8001`
- Модель: `grok-imagine-1.0`/`grok-imagine-1.0`

## Переменные окружения

> Файл конфигурации `.env`

| Переменная | Описание | По умолчанию | Пример |
| :-- | :-- | :-- | :-- |
| `LOG_LEVEL` | Уровень логирования | `INFO` | `DEBUG` |
| `LOG_FILE_ENABLED` | Включить файловые логи | `true` | `false` |
| `DATA_DIR` | Директория данных (конфиг/токены/блокировки) | `./data` | `/data` |
| `SERVER_HOST` | Адрес прослушивания | `0.0.0.0` | `0.0.0.0` |
| `SERVER_PORT` | Порт сервиса | `8000` | `8000` |
| `HOST_PORT` | Порт хост-машины (Docker Compose) | `8000` | `9000` |
| `SERVER_WORKERS` | Количество воркеров | `1` | `2` |
| `SERVER_STORAGE_TYPE` | Тип хранилища (`local`/`redis`/`mysql`/`pgsql`) | `local` | `pgsql` |
| `SERVER_STORAGE_URL` | Строка подключения (пусто для local) | `""` | `postgresql+asyncpg://user:password@host:5432/db` |

> MySQL пример: `mysql+aiomysql://user:password@host:3306/db` (если указать `mysql://` — автоматически преобразуется в `mysql+aiomysql://`)

---

## Доступные запросы

- **Basic аккаунт:** 80 запросов / 20 часов
- **Super аккаунт:** 140 запросов / 2 часа

---

## Доступные модели

| Модель | Стоимость | Аккаунт | Чат | Изображения | Видео |
| :-- | :--: | :-- | :--: | :--: | :--: |
| `grok-3` | 1 | Basic/Super | ✅ | ✅ | — |
| `grok-3-mini` | 1 | Basic/Super | ✅ | ✅ | — |
| `grok-3-thinking` | 1 | Basic/Super | ✅ | ✅ | — |
| `grok-4` | 1 | Basic/Super | ✅ | ✅ | — |
| `grok-4-thinking` | 1 | Basic/Super | ✅ | ✅ | — |
| `grok-4-heavy` | 4 | Super | ✅ | ✅ | — |
| `grok-4.1-mini` | 1 | Basic/Super | ✅ | ✅ | — |
| `grok-4.1-fast` | 1 | Basic/Super | ✅ | ✅ | — |
| `grok-4.1-expert` | 4 | Basic/Super | ✅ | ✅ | — |
| `grok-4.1-thinking` | 4 | Basic/Super | ✅ | ✅ | — |
| `grok-4.20-beta` | 1 | Basic/Super | ✅ | ✅ | — |
| `grok-imagine-1.0` | — | Basic/Super | — | ✅ | — |
| `grok-imagine-1.0-fast` | — | Basic/Super | — | ✅ | — |
| `grok-imagine-1.0-edit` | — | Basic/Super | — | ✅ | — |
| `grok-imagine-1.0-video` | — | Basic/Super | — | — | ✅ |

---

## API-эндпоинты

> В примерах используется `localhost:8001`; если в Docker Compose задан `HOST_PORT` — замените на соответствующий порт.

### `POST /v1/chat/completions`

Универсальный эндпоинт — чат, генерация/редактирование изображений, генерация видео.

```bash
curl http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $GROK2API_API_KEY" \
  -d '{
    "model": "grok-4",
    "messages": [{"role":"user","content":"Привет!"}]
  }'
```

Основные параметры: `model`, `messages`, `stream`, `reasoning_effort`, `temperature`, `top_p`, `tools`, `tool_choice`, `image_config`, `video_config`. Подробнее — см. оригинальную документацию.

### `POST /v1/images/generations`

Генерация изображений.

```bash
curl http://localhost:8001/v1/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $GROK2API_API_KEY" \
  -d '{
    "model": "grok-imagine-1.0",
    "prompt": "кот, парящий в космосе",
    "n": 1
  }'
```

Поддерживаемые размеры: `1024x1024`, `1280x720`, `720x1280`, `1792x1024`, `1024x1792`.

### `POST /v1/images/edits`

Редактирование изображений (multipart/form-data).

```bash
curl http://localhost:8000/v1/images/edits \
  -H "Authorization: Bearer $GROK2API_API_KEY" \
  -F "model=grok-imagine-1.0-edit" \
  -F "prompt=сделай картинку чётче" \
  -F "image=@/путь/к/картинке.png" \
  -F "n=1"
```

### `POST /v1/responses`

OpenAI Responses API — совместимый эндпоинт.

```bash
curl http://localhost:8000/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $GROK2API_API_KEY" \
  -d '{
    "model": "grok-4",
    "input": "Объясни квантовое туннелирование",
    "stream": true
  }'
```

---

## Использование с SillyTavern

Grok2API полностью совместим с SillyTavern через OpenAI-совместимый формат.

### Подключение для чата

1. В SillyTavern: API → Chat Completion → Custom (OpenAI-compatible)
2. Custom Endpoint: `http://localhost:8000/v1`
3. Модель: `grok-4` (или любая другая из списка)

---

## Конфигурация

Файл: `data/config.toml`

> В продакшене или при использовании реверс-прокси убедитесь, что `app.app_url` указывает на корректный внешний URL, иначе ссылки на файлы могут не работать.

Полная таблица параметров доступна в [оригинальной документации](https://blog.cheny.me/blog/posts/grok2api).

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Chenyme/grok2api&type=Timeline)](https://star-history.com/#Chenyme/grok2api&Timeline)
