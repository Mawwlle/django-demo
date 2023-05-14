from random import choice

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404
from payments.models import Account, Transaction
from rest_framework import serializers
from rest_framework.validators import UniqueValidator


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    password_repeat = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = (
            "username",
            "password",
            "password_repeat",
            "email",
            "first_name",
            "last_name",
        )
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password_repeat"]:
            raise serializers.ValidationError({"password": "Password fields didn't match!"})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )

        user.set_password(validated_data["password"])
        user.save()

        return user


class UserSerializer(serializers.HyperlinkedModelSerializer):
    accounts = serializers.PrimaryKeyRelatedField(many=True, queryset=Account.objects.all())

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "accounts"]


class AccountSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Account
        fields = ["id", "balance", "name", "owner"]


class TransactionSerializer(serializers.ModelSerializer):
    date = serializers.ReadOnlyField()

    class Meta:
        model = Transaction
        fields = ["id", "account", "recipient", "amount", "date"]

    def create(self, validated_data):
        account = validated_data["account"]
        recipient_id = validated_data["recipient"]
        amount = validated_data["amount"]
        sender = get_object_or_404(Account, pk=account.id)
        recipient = get_object_or_404(Account, id=recipient_id)

        if sender.balance - amount < 0:
            raise serializers.ValidationError("Too much amount! Can't create a transaction!")

        sender.balance -= amount
        recipient.balance += amount

        sender.save()
        recipient.save()

        transaction = Transaction.objects.create(
            account=account, recipient=recipient_id, amount=validated_data["amount"]
        )

        transaction.save()

        return transaction
