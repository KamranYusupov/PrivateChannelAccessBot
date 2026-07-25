from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class FaceRatesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web.apps.face_rates'
    verbose_name = _('Рейты лиц')
