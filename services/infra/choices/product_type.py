from enum import Enum
from typing import Type, Optional

from common.typing import TariffModelT
from services.infra.choices.base import ChoicesBaseHelper
from web.apps.consultations.models import ConsultationTariff
from web.apps.face_rates.models import FaceRateTariff
from web.apps.payments.models import ProductType
from web.apps.subscriptions.models import PrivateChannelTariff


class ProductTypeHelper(ChoicesBaseHelper):
    __product_type_model_map = {
        ProductType.FACE_RATE.value: FaceRateTariff,
        ProductType.CONSULTATION.value: ConsultationTariff,
        ProductType.PRIVATE_CHANNEL_ACCESS.value: PrivateChannelTariff
    }

    @classmethod
    def get_tariff_model_by_value(
            cls,
            value: str,
    ) -> Optional[Type[TariffModelT]]:
        return cls.__product_type_model_map.get(value)


product_type_helper = ProductTypeHelper(
    choices=ProductType,
)



