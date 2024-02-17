from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from book_service.models import Book
from borrowing_service.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "expected_return_date", "book", "user")
        read_only_fields = ("id", "user")

    def validate(self, attrs):
        data = super(BorrowingSerializer, self).validate(attrs=attrs)
        Borrowing.validate_book_data(attrs["book"], ValidationError)
        return data


class BorrowingListSerializer(serializers.ModelSerializer):
    book = serializers.SlugRelatedField(read_only=True, slug_field="title")
    user = serializers.SlugRelatedField(read_only=True, slug_field="email")
    class Meta:
        model = Borrowing
        fields = ("id", "borrowing_date", "expected_return_date", "actual_return", "book", "user")


class PostSerializer(serializers.Serializer):
    pass
