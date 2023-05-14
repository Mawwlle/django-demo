from cgitb import lookup

from django.urls import include, path
from payments import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r"accounts", views.AccountViewSet, basename="accounts")
router.register(r"users", views.UserViewSet, basename="users")
router.register(r"transactions", views.TransactionsViewSet, basename="users")


urlpatterns = [
    path(r"", include(router.urls)),
]
