from typing import Tuple, Any, Callable, Optional, Iterable, Mapping, Dict

from celery import Task

from infrastructure.adapters.telegram.exceptions import (
    TelegramAPIError,
    TelegramRetryAfter,
    TelegramBadRequest,
    TelegramNetworkError,
)


def execute_with_telegram_retry(
        task: Task,
        telegram_bot_method: Callable,
        task_args: Optional[Tuple] = None,
        task_kwargs: Optional[Dict[str, Any]] = None,
        telegram_bot_method_args: Optional[Iterable[Any]] = None,
        telegram_bot_method_kwargs: Optional[Mapping[str, Any]] = None,
):
    if task_args is None:
        task_args = ()
    if task_kwargs is None:
        task_kwargs = {}
    if telegram_bot_method_args is None:
        telegram_bot_method_args = ()
    if telegram_bot_method_kwargs is None:
        telegram_bot_method_kwargs = {}

    try:
        return telegram_bot_method(
            *telegram_bot_method_args,
            **telegram_bot_method_kwargs
        )
    except (TelegramNetworkError, TelegramRetryAfter) as e:
        countdown = 0
        if isinstance(e, TelegramRetryAfter):
            countdown = e.retry_after

        raise task.retry(
            args=task_args,
            kwargs=task_kwargs,
            countdown=countdown
        )
    except TelegramAPIError:
        raise

