import stripe
from django.db import transaction
from django.shortcuts import redirect
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from book_service.models import Book
from borrowing_service.models import Borrowing
from borrowing_service.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    PostSerializer,
)
from library import settings
from notifications_service.tasks import new_borrowing_created
from payment_service.models import PaymentRequired


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    authentication_classes = (TokenAuthentication, JWTAuthentication)
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = Borrowing.objects.all()
        user_id = self.request.query_params.get("user_id")
        is_active = self.request.query_params.get("is_active")

        if user_id:
            queryset = queryset.filter(user__id=user_id)
        if is_active == "true":
            queryset = queryset.filter(actual_return__isnull=True)
        if is_active == "false":
            queryset = queryset.filter(actual_return__isnull=False)
        return queryset

    def get_serializer_class(self):
        if self.action in ("create", "retrive"):
            return BorrowingSerializer
        if self.action == "return_book":
            return PostSerializer
        return BorrowingListSerializer

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            book = Book.objects.get(pk=request.POST.get("book"))
            if book.inventory > 0:
                book.inventory -= 1
                book.save()
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            new_borrowing_created(serializer.data["id"])
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )

    @action(
        methods=["POST"],
        detail=True,
        url_path="return",
        permission_classes=[IsAuthenticated],
    )
    def return_book(self, request, *args, **kwargs):
        with transaction.atomic():
            borrow = self.get_object()
            if borrow.actual_return:
                return Response(
                    data={"return": "This borrow already returned"},
                    status=status.HTTP_202_ACCEPTED,
                )
            borrow.actual_return = timezone.now().date()

            type = (
                "PAYMENT"
                if borrow.actual_return < borrow.expected_return_date
                else "FINE"
            )

            book = Book.objects.get(pk=borrow.book.pk)
            book.inventory += 1

            stripe.api_key = settings.STRIPE_SECRET_KEY
            domen = "http://127.0.0.1:8000/"

            days = (borrow.actual_return - borrow.borrowing_date).days

            payment_amount = (
                days * borrow.book.daily_fee
                if type == "PAYMENT"
                else days * borrow.book.daily_fee * settings.FINE_MULTIPLIER
            )

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "eur",
                            "unit_amount": payment_amount * 100,
                            "product_data": {"name": str(borrow)},
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=domen
                + redirect(
                    "payment_service:paymentrequired-success", pk=self.get_object().pk
                ).url,
                cancel_url=domen
                + redirect(
                    "payment_service:paymentrequired-cancel", pk=self.get_object().pk
                ).url,
            )

            PaymentRequired.objects.create(
                type=type,
                borrow=borrow,
                session_url=checkout_session.url,
                session_id=checkout_session.id,
                money_to_paid=payment_amount,
            )
            borrow.save()
            book.save()
        return Response(
            data={"return": f"you succsesful return {book.title}"},
            status=status.HTTP_202_ACCEPTED,
        )
