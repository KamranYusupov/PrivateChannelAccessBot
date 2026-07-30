from typing import Dict, Any, Optional

from django.db.models import Manager
from utils.iter import batched

def update_by_batches(
        manager: Manager,
        update_kwargs: Dict[str, Any],
        filters: Optional[Dict[str, Any]] = None,
        batch_size: int = 500,

) -> int:
    updated_count = 0

    if filters:
        select_statement = manager.filter(**filters)
    else:
        select_statement = manager.all()

    ids_count = select_statement.count()

    if ids_count == 0:
        return updated_count

    for offset in range(0, ids_count, batch_size):
        ids = list(
            select_statement
            .values_list('id', flat=True)[offset:offset + batch_size]
        )
        updated_count += manager.filter(id__in=ids).update(
            **update_kwargs
        )

    return updated_count