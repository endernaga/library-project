from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from book_service.models import Book
from book_service.serializers import BookSerializer
from borrowing_service.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    return_url = serializers.URLField(read_only=True, source="get_return_url")

    class Meta:
        model = Borrowing
        fields = ("id", "expected_return_date", "book", "user", "return_url")
        read_only_fields = ("id", "user")

    def validate(self, attrs):
        data = super(BorrowingSerializer, self).validate(attrs=attrs)
        Borrowing.validate_book_data(attrs["book"], ValidationError)
        return data


class BorrowingListSerializer(BorrowingSerializer):
    book = BookSerializer(read_only=True)
    user = serializers.SlugRelatedField(read_only=True, slug_field="email")

    class Meta(BorrowingSerializer.Meta):
        model = Borrowing
        fields = (
            "id",
            "return_url",
            "borrowing_date",
            "expected_return_date",
            "actual_return",
            "book",
            "user",
        )


class PostSerializer(serializers.Serializer):
    pass
