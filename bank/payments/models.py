from django.db import models


class Account(models.Model):
    owner = models.ForeignKey("auth.User", related_name="accounts", on_delete=models.CASCADE)
    balance = models.FloatField(default=0)
    name = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(balance__gt=0),
                name="check_balance",
            ),
        ]


class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    recipient = models.PositiveBigIntegerField()
    amount = models.FloatField(default=0)
    date = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gt=0),
                name="check_amount",
            ),
        ]
