from typing import Optional

from django.db.models.query import QuerySet

from common.typing import ModelT


async def aget_or_none(qs: QuerySet[ModelT], **kwargs) -> Optional[ModelT]:
    try:
        return await qs.aget(**kwargs)
    except qs.model.DoesNotExist:
        return None