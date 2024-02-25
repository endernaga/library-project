import json

import stripe
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from library import settings
from payment_service.models import PaymentRequired
from payment_service.serializers import PaymentSerializer
from rest_framework import mixins, viewsets, status


# Create your views here.


@csrf_exempt
@permission_classes([AllowAny])
@api_view(["POST"])
def my_webhook_view(request):
    try:
        event = json.loads(request.body)
    except json.decoder.JSONDecodeError as e:
        print("⚠️  Webhook error while parsing basic request." + str(e))
        return Response({"success": "false"}, status=status.HTTP_400_BAD_REQUEST)

    if event and event["type"] == "checkout.session.completed":
        payment = PaymentRequired.objects.get(
            session_id=event.get("data").get("object").get("id")
        )
        payment.status = "PAID"
        payment.save()
        # Then define and call a method to handle the successful payment intent.
        # handle_payment_intent_succeeded(payment_intent)
    elif event["type"] == "payment_method.attached":
        payment_method = event["data"]["object"]  # contains a stripe.PaymentMethod
        # Then define and call a method to handle the successful attachment of a PaymentMethod.
        # handle_payment_method_attached(payment_method)
    else:
        # Unexpected event type
        print("Unhandled event type {}".format(event["type"]))

    return Response(data={"success": "true"}, status=status.HTTP_200_OK)


class CreatePayment(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    serializer_class = PaymentSerializer
    queryset = PaymentRequired.objects.all().filter()
    authentication_classes = (TokenAuthentication, JWTAuthentication)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = PaymentRequired.objects.filter(borrow__user__pk=self.request.user.pk)
        if self.action == "GET":
            queryset = queryset.filter(status="PENDING")
        return queryset

    @action(
        methods=["GET"], detail=True, url_path="succses", permission_classes=(AllowAny,)
    )
    def success(self, request, *args, **kwargs):
        return Response(data={"success": True}, status=status.HTTP_200_OK)

    @action(
        methods=["GET"], detail=True, url_path="cancel", permission_classes=(AllowAny,)
    )
    def cancel(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.retrieve(
            self.get_object().session_id
        )
        error = stripe.PaymentIntent.retrieve(session.get("payment_intent")).get("last_payment_error")
        if error:
            return Response(
                data={"success": False, "error": error.type}, status=status.HTTP_200_OK
            )
        return redirect("payment_service:paymentrequired-success", pk=self.get_object().pk)