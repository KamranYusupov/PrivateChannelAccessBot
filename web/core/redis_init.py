from functools import wraps

import redis
import loguru
from celery import shared_task, Task
from django.conf import settings


redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_RATE_LIMIT_DB,
    decode_responses=True,
)

# LUA-скрипт для атомарной проверки лимита (алгоритм Fixed Window).
RATE_LIMIT_LUA_SCRIPT = """
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window_seconds = tonumber(ARGV[2])

-- Увеличиваем счетчик запросов
local current = redis.call('INCR', key)

-- Если это первый запрос в этом окне, ставим время жизни ключа (TTL)
if current == 1 then
    redis.call('EXPIRE', key, window_seconds)
end

-- Проверяем, не пробили ли мы лимит
if current > limit then
    return 0 -- Лимит превышен (False)
else
    return 1 -- Можно делать запрос (True)
end
"""

check_rate_limit_script = redis_client.register_script(RATE_LIMIT_LUA_SCRIPT)


def is_rate_limited(key: str, limit: int, window: int = 1) -> bool:
    """
    Проверяет глобальный лимит в Redis.
    Возвращает True, если лимит превышен.
    """
    result = check_rate_limit_script(keys=[key], args=[limit, window])
    return result == 0


def task_rate_limit(key: str, limit: int, window: int = 1):
    """
    Декоратор лимита выполняемых Celery задач.
    Обязателен bind=True с передачей self в аргументы задачи.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if is_rate_limited(key, limit, window):
                loguru.logger.debug(
                    f"Global rate limit hit for task '{func.__name__}'. Retrying in 1s..."
                )
                raise self.retry(countdown=1)

            return func(self, *args, **kwargs)

        return wrapper

    return decorator

def telegram_api_task_rate_limit():
    return task_rate_limit(
        key=settings.TELEGRAM_API_TASKS_RATE_LIMIT_KEY,
        limit=settings.TELEGRAM_API_TASKS_RATE_LIMIT,
        window=settings.TELEGRAM_API_TASKS_RATE_LIMIT_WINDOW
    )
