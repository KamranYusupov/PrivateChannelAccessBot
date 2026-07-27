from enum import Enum
from typing import Type, Optional

from common.typing import TariffModelT
from web.apps.consultations.models import ConsultationTariff
from web.apps.face_rates.models import FaceRateTariff
from web.apps.payments.models import ProductType
from web.apps.subscriptions.models import PrivateChannelTariff



class ProductTypeService:
    __product_type_model_map = {
        ProductType.FACE_RATE.value: FaceRateTariff,
        ProductType.CONSULTATION.value: ConsultationTariff,
        ProductType.PRIVATE_CHANNEL_ACCESS.value: PrivateChannelTariff
    }

    __product_type_to_label_map = {
        product_type.label: product_type
        for product_type in ProductType
    }
    __product_type_to_value_map = {
        product_type.value: product_type
        for product_type in ProductType
    }

    @classmethod
    def get_product_type_by_label(
            cls,
            label: str,
    ) -> Optional[ProductType]:
        return cls.__product_type_to_label_map.get(label)

    @classmethod
    def get_product_type_by_value(
            cls,
            value: str,
    ) -> Optional[ProductType]:
        return cls.__product_type_to_value_map.get(value)

    @classmethod
    def get_tariff_model_by_product_type_value(
            cls,
            value: str,
    ) -> Optional[Type[TariffModelT]]:
        return cls.__product_type_model_map.get(value)




