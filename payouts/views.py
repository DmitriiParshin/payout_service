from typing import Any

from rest_framework import viewsets, status
from rest_framework.request import Request
from rest_framework.response import Response
from payouts.models import Payout, RecipientDetails, Currency
from payouts.serializers import PayoutSerializer, CurrencySerializer, RecipientDetailsSerializer
from payouts.tasks import process_payout_task


class CurrencyViewSet(viewsets.ModelViewSet):
    """ViewSet для управления валютами"""
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    lookup_field = 'id'


class RecipientDetailsViewSet(viewsets.ModelViewSet):
    """ViewSet для управления реквизитами получателя"""
    queryset = RecipientDetails.objects.all()
    serializer_class = RecipientDetailsSerializer
    lookup_field = 'id'


class PayoutViewSet(viewsets.ModelViewSet):
    """ViewSet для управления заявками на выплату"""
    queryset = Payout.objects.select_related(
        'currency', 'recipient_details'
    ).all()
    serializer_class = PayoutSerializer
    lookup_field = 'id'

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Создание заявки с запуском Celery задачи"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payout = serializer.save()

        # Запуск асинхронной обработки
        process_payout_task.delay(str(payout.id))

        out = PayoutSerializer(payout, context={'request': request}).data
        headers = self.get_success_headers(out)
        return Response(out, status=status.HTTP_201_CREATED, headers=headers)

    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Частичное обновление заявки"""
        payout = self.get_object()

        # Разрешаем обновление только определенных полей
        allowed_fields = ['status', 'description', 'error_message']
        data = {
            k: v for k, v in request.data.items()
            if k in allowed_fields
        }

        serializer = self.get_serializer(payout, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()

        return Response(PayoutSerializer(updated, context={'request': request}).data)

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Удаление: в ответе возвращаем сериализованный объект (до удаления)"""
        instance = self.get_object()
        data = PayoutSerializer(instance, context={'request': request}).data
        self.perform_destroy(instance)
        return Response(data, status=status.HTTP_200_OK)
