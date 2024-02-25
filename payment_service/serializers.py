import datetime

from rest_framework import serializers

from borrowing_service.serializers import BorrowingListSerializer
from payment_service.models import PaymentRequired


class PaymentSerializer(serializers.ModelSerializer):
    borrow = BorrowingListSerializer(read_only=True, many=False)
    payment_session_url = serializers.URLField(read_only=True, source="session_url")
    payment_session_id = serializers.CharField(read_only=True, source="session_id")

    class Meta:
        model = PaymentRequired
        fields = ("id", "status", "type", "borrow", "payment_session_url", "payment_session_id", "money_to_paid")
