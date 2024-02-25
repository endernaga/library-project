from django.urls import path, include
from rest_framework import routers

from payment_service.views import CreatePayment, my_webhook_view

router = routers.DefaultRouter()
router.register("", CreatePayment)

urlpatterns = [
    path("pay/", include(router.urls)),
    path("webhooks", my_webhook_view, name="webhooks"),
]

app_name = "payment_service"
