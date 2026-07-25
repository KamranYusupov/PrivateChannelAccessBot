from django.contrib import admin

from web.apps.face_rates.models import FaceRate, FaceRatePhoto, FaceRateTariff


@admin.register(FaceRate)
class AdminFaceRate(admin.ModelAdmin):
    pass


@admin.register(FaceRateTariff)
class AdminFaceRateTariff(admin.ModelAdmin):
    pass