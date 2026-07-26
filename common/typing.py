from typing import TypeVar

from django.db import models

from web.db.model_mixins import AbstractTariff

ModelT = TypeVar('ModelT', bound=models.Model)
TariffModelT = TypeVar('TariffModelT', bound=AbstractTariff)