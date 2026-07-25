from enum import Enum
from typing import TypeVar, Type

from web.apps.consultations.models import ConsultationTariff
from web.apps.face_rates.models import FaceRateTariff
from web.apps.payments.models import ProductType
from web.apps.subscriptions.models import PrivateChannelTariff
from web.db.model_mixins import AsyncBaseModel

ModelType = TypeVar('ModelType', bound=AsyncBaseModel)


class ProductCallbackService:
    __product_type_model_map = {
        ProductType.FACE_RATE.label: FaceRateTariff,
        ProductType.CONSULTATION.label: ConsultationTariff,
        ProductType.PRIVATE_CHANNEL_ACCESS.label: PrivateChannelTariff
    }

    __product_type_label_to_value_map = {
        product_type.label: product_type.value
        for product_type in ProductType
    }
    __product_type_value_to_label_map = {
        product_type.value: product_type.label
        for product_type in ProductType
    }

    @classmethod
    def get_tariff_model_by_product_type_label(
            cls,
            product_type_label: str,
    ) -> Type[ModelType] | None:
        return cls.__product_type_model_map.get(product_type_label)

    @classmethod
    def get_product_type_value_by_label(
            cls,
            product_type_label: str,
    ) -> Type[ModelType] | None:
        return cls.__product_type_label_to_value_map.get(product_type_label)

    @classmethod
    def get_product_type_label_by_value(
            cls,
            product_type_value: str,
    ) -> Type[ModelType] | None:
        return cls.__product_type_value_to_label_map.get(product_type_value)




