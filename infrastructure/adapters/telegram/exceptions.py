
class TelegramAPIError(Exception):
    def __init__(self, message: str, error_code: int):
        self.message = message
        self.error_code = error_code
        super().__init__()

class TelegramBadRequest(TelegramAPIError): ...

class TelegramRetryAfter(TelegramAPIError):
    def __init__(self, error_code: int, retry_after: int):
        self.retry_after = retry_after
        super().__init__(
            message=f'Retry after {retry_after}s',
            error_code=error_code,
        )

class TelegramNetworkError(TelegramAPIError): ...

class TelegramForbidden(TelegramAPIError): ...