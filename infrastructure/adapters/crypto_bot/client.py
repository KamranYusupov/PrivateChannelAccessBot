from decimal import Decimal
from typing import Dict, Optional, Any, Tuple

import aiohttp
import loguru
from django.conf import settings


class CryptoBotAPIClient:

    def __init__(
        self,
        base_url: str = settings.CRYPTO_BOT_API_BASE_URL,
        api_token: str = settings.CRYPTO_BOT_API_TOKEN,
    ):
        self.base_url = base_url
        self.__api_token = api_token

    async def _request(
        self,
        http_method: str,
        api_method: str,
        payload: Dict[str, Any],
        timeout: int = 10,
    ) -> Dict[str, Any]:
        headers = {'Crypto-Pay-API-Token': self.__api_token}
        request_kwargs = {
            'headers': headers,
            'timeout': timeout,
        }

        http_method_upper = http_method.upper()
        if http_method_upper == 'GET':
            request_kwargs['params'] = payload
        elif http_method_upper in ('POST', 'PUT', 'PATCH', 'DELETE'):
            request_kwargs['json'] = payload

        async with aiohttp.ClientSession() as session:
            async with session.request(
                    http_method,
                    f'{self.base_url}{api_method}',
                    **request_kwargs,
            ) as resp:
                return await resp.json()

    async def _request_get(
            self,
            api_method: str,
            params: Optional[Dict[str, Any]] = None,
            timeout: int = 10,
    ) -> Dict[str, Any]:
        params = params or {}
        return await self._request(
            'GET', api_method, params, timeout,
        )

    async def _request_post(
            self,
            api_method: str,
            payload: Dict[str, Any],
            timeout: int = 10,
    ) -> Dict[str, Any]:
        return await self._request(
            'POST', api_method, payload, timeout,
        )

    async def create_invoice(
            self,
            *,
            amount: Decimal,
            currency_type: str = 'crypto',
            asset: Optional[str] = 'USDT',
            fiat: Optional[str] = None,
            accepted_assets: Optional[str] = None,
            swap_to: Optional[str] = None,
            description: Optional[str] = None,
            hidden_message: Optional[str] = None,
            paid_btn_name: Optional[str] = None,
            paid_btn_url: Optional[str] = None,
            payload: Optional[str] = None,
            allow_comments: Optional[bool] = None,
            allow_anonymous: Optional[bool] = None,
            expires_in: Optional[int] = None,
    ) -> Dict[str, Any]:
        request_data = {
            'currency_type': currency_type,
            'amount': str(amount),
        }

        optional_fields = {
            'asset': asset,
            'fiat': fiat,
            'accepted_assets': accepted_assets,
            'swap_to': swap_to,
            'description': description,
            'hidden_message': hidden_message,
            'paid_btn_name': paid_btn_name,
            'paid_btn_url': paid_btn_url,
            'payload': payload,
            'allow_comments': allow_comments,
            'allow_anonymous': allow_anonymous,
            'expires_in': expires_in,
        }

        request_data.update(
            {k: v for k, v in optional_fields.items() if v is not None}
        )

        return await self._request_post(
            'createInvoice',
            payload=request_data,
        )

    async def get_invoices(self) -> Dict[str, Any]:
        method = 'getInvoices'
        return await self._request_get(method)

    async def get_invoice_by_id(self, invoice_id: int) -> Optional[Dict]:
        response_data = await self.get_invoices()
        invoices = response_data.get('result', {}).get('items')

        if not invoices:
            return None

        for iv in invoices:
            if iv['invoice_id'] == invoice_id:
                return iv

        return None