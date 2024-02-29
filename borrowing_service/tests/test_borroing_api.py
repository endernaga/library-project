from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from book_service.models import Book
from book_service.serializers import BookSerializer
from borrowing_service.models import Borrowing
from borrowing_service.serializers import BorrowingListSerializer


def sample_book(**params):
    defaults = {
        "title": "test",
        "author": "test",
        "cover": "Soft",
        "inventory": 10,
        "daily_fee": 2,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def sample_borrowing(book, user, **params):
    defaults = {
        "borrowing_date": date.today(),
        "expected_return_date": date.today() + timedelta(days=5),
        "book": book,
        "user": user,
    }
    defaults.update(**params)
    return Borrowing.objects.create(**defaults)


BORROWINGS_URL = reverse("borrowing_service:borrowing-list")


class UnauthenticatedBookApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_get_borrowings_status_code_400(self):
        page = self.client.get(BORROWINGS_URL)
        self.assertEqual(page.status_code, 401)


class AuthenticatedBookApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@gmail.com", password="user12345"
        )
        self.client.force_authenticate(user=self.user)

    def test_get_borrowings(self):
        book = sample_book()
        borrowing = sample_borrowing(book, self.user)
        page = self.client.get(BORROWINGS_URL)
        borrowing_data = BorrowingListSerializer(borrowing)
        self.assertEqual(page.status_code, 200)
        self.assertEqual(page.data["results"][0], borrowing_data.data)

    def test_create_borrowing(self):
        book = sample_book()
        data = {
            "borrowing_date": date.today(),
            "expected_return_date": date.today() + timedelta(days=5),
            "book": book.pk,
            "user": self.user.pk,
        }
        page = self.client.post(BORROWINGS_URL, data)
        self.assertEqual(page.status_code, 201)

    def test_return_borrowing(self):
        book = sample_book()
        sample_borrowing(book, self.user)
        page = self.client.post(BORROWINGS_URL + "1/return/")
        page2 = self.client.post(BORROWINGS_URL + "1/return/")
        self.assertEqual(page.status_code, 202)
        self.assertEqual(page2.status_code, 400)

