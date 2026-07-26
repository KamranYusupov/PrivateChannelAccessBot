from typing import Any, Dict, Tuple, NoReturn

import requests
from infrastructure.adapters.telegram.exceptions import (
    TelegramAPIError,
    TelegramRetryAfter,
    TelegramBadRequest,
    TelegramForbidden,
    TelegramNetworkError,
)

class TelegramBotSyncClient:

    def __init__(self, token: str):
        self.base_url = (
            f'https://api.telegram.org/bot{token}'
        )

    @staticmethod
    def _raise_error(response_data: Dict[str, Any]) -> NoReturn:
        exc_data = {
            'message': response_data['description'],
            'error_code': response_data['error_code'],
        }
        match response_data['error_code']:
            case 400:
                raise TelegramBadRequest(**exc_data)
            case 429:
                raise TelegramRetryAfter(
                    **exc_data,
                    retry_after=response_data['parameters']['retry_after'],
                )
            case 403:
                raise TelegramForbidden(**exc_data)
            case _:
                raise TelegramAPIError(**exc_data)

    def _post_request(
            self,
            method: str,
            payload: Dict[str, Any],
            timeout: int | Tuple[int, int] = (3, 10),
    ) -> Dict[str, Any]:
        try:
            response = requests.post(
                f'{self.base_url}/{method}',
                json=payload,
                timeout=timeout
            )
        except requests.RequestException as e:
            raise TelegramNetworkError() from e

        data = response.json()

        if not data['ok']:
            self._raise_error(data)

        return data['result']


    def create_chat_invite_link(
        self,
        chat_id: int,
        member_limit: int = 1,
    ) -> str:
        result = self._post_request(
            'createChatInviteLink',
            payload={
                'chat_id': chat_id,
                'member_limit': member_limit,
            },
        )

        return result['invite_link']


    def send_message(
        self,
        chat_id: int,
        text: str,
    ) -> Dict[str, Any]:
        result = self._post_request(
            'sendMessage',
            payload={
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML',
            },
        )

        return result