from django.contrib import admin

from web.apps.consultations.models import Consultation, ConsultationTariff


@admin.register(Consultation)
class AdminConsultation(admin.ModelAdmin):
    pass


@admin.register(ConsultationTariff)
class AdminConsultationTariff(admin.ModelAdmin):
    pass