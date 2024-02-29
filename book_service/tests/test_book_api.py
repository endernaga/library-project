from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from book_service.models import Book
from book_service.serializers import BookSerializer


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


BOOK_URL = reverse("book_service:book-list")


class UnauthenticatedBookApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_get_books_status_code_200(self):
        book = sample_book()
        page = self.client.get(BOOK_URL)
        page_content = BookSerializer(book)
        self.assertEqual(page.status_code, 200)
        self.assertEqual(page.data["results"][0], page_content.data)

    def test_cancel_create_book(self):
        page = self.client.post(
            BOOK_URL,
            {
                "title": "test",
                "author": "test",
                "cover": "Soft",
                "inventory": 10,
                "daily_fee": 2,
            },
        )
        self.assertEqual(page.status_code, 401)


class AuthenticatedBookApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            email="user@gmail.com", password="user12345"
        )
        self.client.force_authenticate(user)

    def test_cancel_create_book(self):
        page = self.client.post(
            BOOK_URL,
            {
                "title": "test",
                "author": "test",
                "cover": "Soft",
                "inventory": 10,
                "daily_fee": 2,
            },
        )
        self.assertEqual(page.status_code, 403)


class AdminBookApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        user = get_user_model().objects.create_superuser(
            email="admin@gmail.com", password="admin12345"
        )
        self.client.force_authenticate(user)

    def test_create_book(self):
        page = self.client.post(
            BOOK_URL,
            {
                "title": "test",
                "author": "test",
                "cover": "Soft",
                "inventory": 10,
                "daily_fee": 2,
            },
        )
        self.assertEqual(page.status_code, 201)
