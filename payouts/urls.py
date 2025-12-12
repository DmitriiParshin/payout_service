from django.urls import path, include
from rest_framework.routers import DefaultRouter

from payouts.views import PayoutViewSet, CurrencyViewSet, RecipientDetailsViewSet

router = DefaultRouter()
router.register(r'payouts', PayoutViewSet, basename='payout')
router.register(r'currencies', CurrencyViewSet, basename='currency')
router.register(r'recipients', RecipientDetailsViewSet, basename='recipient')

urlpatterns = [
    path('api/', include(router.urls)),
]
