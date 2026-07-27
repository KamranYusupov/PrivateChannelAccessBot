from django.urls import include, path

urlpatterns = [
    path('payments/', include('web.api.v1.payments.urls')),
]