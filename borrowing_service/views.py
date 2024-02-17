from django.db import transaction
from django.shortcuts import render
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from book_service.models import Book
from borrowing_service.models import Borrowing
from borrowing_service.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    PostSerializer,
)


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = Borrowing.objects.all()
        user_id = self.request.query_params.get('user_id')
        is_active = self.request.query_params.get('is_active')

        if user_id:
            queryset = queryset.filter(user__id=user_id)
        if is_active == 'true':
            queryset = queryset.filter(actual_return__isnull=True)
        if is_active == 'false':
            queryset = queryset.filter(actual_return__isnull=False)
        return queryset

    def get_serializer_class(self):
        if self.action == "create":
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
            return super().create(request, *args, **kwargs)

    @action(
        methods=["POST"],
        detail=True,
        url_path="return",
        permission_classes=[IsAuthenticated],
    )
    def return_book(self, request, *args, **kwargs):
        with transaction.atomic():
            book = Book.objects.get(pk=kwargs["pk"])
            book.inventory += 1
            borrow = self.get_object()
            borrow.actual_return = timezone.now().date()
            borrow.save()
            book.save()
        return Response(BorrowingSerializer(borrow), status=status.HTTP_202_ACCEPTED)
