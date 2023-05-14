from django.urls import include, path

urlpatterns = [
    path("", include("payments.urls")),
    path("api-auth/", include("rest_framework.urls")),
]
