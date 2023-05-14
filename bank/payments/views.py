from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from loguru import logger
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

    def get_serializer_class(
        self,
    ):
        if (
            self.action == "create"
        ):  # это только для того, чтобы в browsable api красиво отображалось.
            return RegisterSerializer  # хотелось чтобы регистрация пользователей была через POST /users.
            # хотя может быть было бы правильнее сделать POST /users/register через action
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
        return self.request.user.accounts.all()

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


class TransactionsViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = TransactionSerializer
    permission_classes = [IsAccountTransaction]

    def get_queryset(self):
        accounts = self.request.user.accounts.all().values_list("id", flat=True)
        return Transaction.objects.filter(account__in=accounts)

    def create(self, request):
        logger.debug(f"Starting transaction! {request.data}")

        serializer = TransactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        account_id = serializer.validated_data["account"].id
        recipient_id = serializer.validated_data["recipient"]

        if account_id == recipient_id:
            return Response(
                data="Same sender and recipient account!",
                status=status.HTTP_400_BAD_REQUEST,
            )

        amount = serializer.validated_data["amount"]

        if amount < 0:
            return Response(
                data="Amount cannot be negative!",
                status=status.HTTP_400_BAD_REQUEST,
            )

        sender = get_object_or_404(Account, pk=account_id)
        recipient = get_object_or_404(Account, id=recipient_id)

        if sender.balance - amount < 0:
            return Response(
                data="Sender balance too small. Please decrease amount!",
                status=status.HTTP_400_BAD_REQUEST,
            )

        sender.balance -= amount
        recipient.balance += amount

        sender.save()
        recipient.save()
        serializer.save()

        logger.debug(f"Transaction done!")

        return Response(serializer.data, status=status.HTTP_201_CREATED)
