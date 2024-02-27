import uuid
from django.db import models

from borrowing_service.models import Borrowing


class PaymentRequired(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "PENDING"
        PAID = "PAID"

    class TypeChoices(models.TextChoices):
        PAYMENT = "PAYMENT"
        FINE = "FINE"

    status = models.CharField(
        max_length=50, choices=StatusChoices.choices, default=StatusChoices.PENDING
    )
    type = models.CharField(
        max_length=50, choices=TypeChoices.choices, default=TypeChoices.PAYMENT
    )
    borrow = models.ForeignKey(Borrowing, on_delete=models.CASCADE)
    session_url = models.URLField(max_length=511)
    session_id = models.CharField(max_length=255, unique=True)
    money_to_paid = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.borrow.user.email} must pay {self.money_to_paid}"
