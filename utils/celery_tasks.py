from typing import Tuple, Any, Callable, Optional, Iterable, Mapping, Dict

import loguru
from celery import Task
from celery_once import AlreadyQueued

from infrastructure.adapters.telegram.exceptions import (
    TelegramAPIError,
    TelegramRetryAfter,
    TelegramBadRequest,
    TelegramNetworkError,
)


def execute_with_telegram_retry(
        task: Task,
        telegram_bot_method: Callable,
        telegram_bot_method_args: Optional[Iterable[Any]] = None,
        telegram_bot_method_kwargs: Optional[Mapping[str, Any]] = None,
):
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
        exception_log = (
            f'Retrying {task.name} '
        )

        countdown = 0
        if isinstance(e, TelegramRetryAfter):
            countdown = e.retry_after + 2
            exception_log += (
                f'after {countdown} seconds'
            )

        loguru.logger.warning(exception_log)

        raise task.retry(
            countdown=countdown,
            exc=e,
        )
    except TelegramAPIError:
        raise


def delay_excepting_already_queued(
        task: Task,
        args: Optional[Iterable[Any]] = None,
        kwargs: Optional[Mapping[str, Any]] = None,
):
    if args is None:
        args = ()
    if kwargs is None:
        kwargs = {}

    try:
        task.delay(*args, **kwargs)
    except AlreadyQueued:
        loguru.logger.debug(
            f'Task {task.name} with kwargs {kwargs} already queued. Skipping...',
        )

