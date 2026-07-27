from django.urls import include, path

urlpatterns = [
    path('v1/', include('web.api.v1.urls')),
]