from typing import Any, Dict, Tuple, NoReturn, List

import requests
from django.conf import settings

from infrastructure.adapters.telegram.exceptions import (
    TelegramAPIError,
    TelegramRetryAfter,
    TelegramBadRequest,
    TelegramForbidden,
    TelegramNetworkError,
)


class TelegramBotSyncClient:

    def __init__(
            self,
            bot_token: str = settings.BOT_TOKEN,
            api_url: str = settings.TELEGRAM_API_URL,
    ):
        self.base_url = f'{api_url}/bot{bot_token}/'

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

    def _request(
            self,
            http_method: str,
            api_method: str,
            payload: Dict[str, Any],
            timeout: int | Tuple[int, int] = (10, 30),
    ) -> Dict[str, Any]:
        try:
            response = requests.request(
                http_method,
                f'{self.base_url}{api_method}',
                json=payload,
                timeout=timeout
            )
        except requests.RequestException as e:
            raise TelegramNetworkError() from e

        data = response.json()

        if not data['ok']:
            self._raise_error(data)

        return data['result']

    def _request_post(
            self,
            api_method: str,
            payload: Dict[str, Any],
            timeout: int | Tuple[int, int] = (10, 30),
    ) -> Dict[str, Any]:
        return self._request(
            'POST',
            api_method,
            payload,
            timeout
        )

    def create_chat_invite_link(
        self,
        chat_id: int,
        member_limit: int = 1,
    ) -> str:
        result = self._request_post(
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
        reply_markup: Dict[str, List[Dict[str, str]]] | None = None,
    ) -> Dict[str, Any]:

        result = self._request_post(
            'sendMessage',
            payload={
                'chat_id': chat_id,
                'text': text,
                'reply_markup': reply_markup,
                'parse_mode': 'HTML',
            },
        )

        return result

    def delete_message(
        self,
        chat_id: int,
        message_id: int,
    ) -> Dict[str, Any]:
        result = self._request_post(
            'deleteMessage',
            payload={
                'chat_id': chat_id,
                'message_id': message_id,
            },
        )

        return result

    def ban_chat_member(
        self,
        chat_id: int,
        user_id: int,
        until_date: int | None = None,
        revoke_messages: bool = False,
    ) -> Dict[str, Any]:

        result = self._request_post(
            'banChatMember',
            payload={
                'chat_id': chat_id,
                'user_id': user_id,
                'until_date': until_date,
                'revoke_messages': revoke_messages,
            },
        )

        return result