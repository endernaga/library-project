from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from book_service.models import Book


class Borrowing(models.Model):
    borrowing_date = models.DateField(auto_now_add=True, editable=False)
    expected_return_date = models.DateField()
    actual_return = models.DateField(blank=True, null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.email} borrow {self.book.title} must return {self.expected_return_date}"

    def clean_book(self):
        book = self.cleaned_data["book"]
        self.validate_book_data(book, ValidationError)
        return book

    @staticmethod
    def validate_book_data(book, error_to_raise):
        if book.inventory <= 0:
            raise error_to_raise("Not enough books to borrowing")
