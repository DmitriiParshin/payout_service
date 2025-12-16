from django.urls import include, path
from rest_framework.routers import DefaultRouter

from payouts.views import PayoutViewSet, RecipientDetailsViewSet


router = DefaultRouter()
router.register(r"payouts", PayoutViewSet, basename="payout")
router.register(r"recipients", RecipientDetailsViewSet, basename="recipient")

urlpatterns = [
    path("api/", include(router.urls)),
]
