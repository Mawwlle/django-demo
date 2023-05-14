from cgitb import lookup

from django.urls import include, path
from payments import views
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

router = DefaultRouter()
router.register(r"accounts", views.AccountViewSet, basename="accounts")
router.register(r"users", views.UserViewSet, basename="users")
transaction_router = routers.NestedSimpleRouter(router, r"accounts", lookup="account")
transaction_router.register(
    r"transactions", views.AccountTransactionsViewSet, basename="account-transactions"
)

urlpatterns = [
    path(r"", include(router.urls)),
    path(r"", include(transaction_router.urls)),
]
