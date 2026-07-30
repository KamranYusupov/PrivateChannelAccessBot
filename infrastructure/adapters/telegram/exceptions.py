from typing import Optional


class TelegramAPIError(Exception):
    def __init__(
            self,
            message: str,
    ):
        super().__init__(message)

class TelegramBadRequest(TelegramAPIError): ...

class TelegramRetryAfter(TelegramAPIError):
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(
            message=f'Retry after {retry_after}s',
        )

class TelegramNetworkError(TelegramAPIError): ...

class TelegramForbidden(TelegramAPIError): ...