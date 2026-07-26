from typing import TypeVar

from django.db import models

ModelT = TypeVar('ModelT', bound=models.Model)
