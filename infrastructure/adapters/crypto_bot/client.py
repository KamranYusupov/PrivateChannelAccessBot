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
        timeout: int | Tuple[int, int] = (3, 10),
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

        async with aiohttp.ClientSession(
            base_url=self.base_url,
        ) as session:
            async with session.request(
                    http_method,
                    api_method,
                    **request_kwargs,
            ) as resp:
                return await resp.json()

    async def _request_get(
            self,
            api_method: str,
            params: Optional[Dict[str, Any]] = None,
            timeout: int | Tuple[int, int] = (3, 10),
    ) -> Dict[str, Any]:
        params = params or {}
        return await self._request(
            'GET', api_method, params, timeout,
        )

    async def _request_post(
            self,
            api_method: str,
            payload: Dict[str, Any],
            timeout: int | Tuple[int, int] = (3, 10),
    ) -> Dict[str, Any]:
        return await self._request(
            'POST', api_method, payload, timeout,
        )

    async def create_invoice(
            self,
            amount: Decimal,
            description: str,
            payload: str,
            asset: str = 'USDT',
    ) -> Dict[str, Any]:
        method = 'createInvoice'
        request_data = {
            'asset': asset,
            'amount': str(amount),
            'description': description,
            'payload': payload,
        }
        return await self._request_post(
            method,
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