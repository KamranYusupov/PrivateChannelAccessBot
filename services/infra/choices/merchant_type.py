from services.infra.choices.base import ChoicesBaseHelper
from web.apps.payments.models import MerchantType


class MerchantTypeHelper(ChoicesBaseHelper[MerchantType]): ...

merchant_type_helper = MerchantTypeHelper(
    choices=MerchantType,
)
