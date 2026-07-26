from typing import Tuple, Any, Callable, Optional, Iterable, Mapping, Dict

from celery import Task, shared_task

from infrastructure.adapters.telegram.exceptions import TelegramAPIError, TelegramRetryAfter


def execute_with_telegram_retry(
        task: Task,
        telegram_bot_method: Callable,
        task_args: Optional[Tuple] = None,
        task_kwargs: Optional[Dict[str, Any]] = None,
        telegram_bot_method_args: Optional[Iterable[Any]] = None,
        telegram_bot_method_kwargs: Optional[Mapping[str, Any]] = None,
):
    task_args = () or task_args
    task_kwargs = {} or task_kwargs
    telegram_bot_method_args = () or telegram_bot_method_args
    telegram_bot_method_kwargs = {} or telegram_bot_method_kwargs

    try:
        return telegram_bot_method(
            *telegram_bot_method_args,
            **telegram_bot_method_kwargs
        )
    except TelegramAPIError as e:
        countdown = 0
        if isinstance(e, TelegramRetryAfter):
            countdown = e.retry_after

        raise task.retry(
            args=task_args,
            kwargs=task_kwargs,
            countdown=countdown
        )

