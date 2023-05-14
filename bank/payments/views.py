from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from payments.models import Account, Transaction
from payments.permissions import IsAccountTransaction, IsOwner, IsReadOnly
from payments.serializers import (
    AccountSerializer,
    RegisterSerializer,
    TransactionSerializer,
    UserSerializer,
)
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return RegisterSerializer

        return self.serializer_class

    def get_permissions(self):
        if self.action == "create":
            permission_classes = []
        else:
            permission_classes = [IsReadOnly]

        return [permission() for permission in permission_classes]


class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    permission_classes = [IsOwner]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        return Account.objects.filter(owner=self.request.user)

    def destroy(self, request, pk=None):
        instance = self.get_object()

        try:
            balance = int(instance.balance)
        except TypeError:
            return Response(data="Incorrect balance value!", status=status.HTTP_400_BAD_REQUEST)

        if balance == 0:
            self.perform_destroy(instance)
            return Response(data="Successfully deleted", status=status.HTTP_200_OK)

        return Response(
            data=f"Balance: {instance.balance}. Deletion available only with 0 balance!",
            status=status.HTTP_412_PRECONDITION_FAILED,
        )


class AccountTransactionsViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = TransactionSerializer
    permission_classes = [IsAccountTransaction]

    def get_queryset(self):
        return Transaction.objects.filter(account=self.kwargs["account_pk"])
