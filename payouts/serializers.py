from django.db import IntegrityError
from rest_framework import serializers

from payouts.models import Currency, Payout, RecipientDetails
from payouts.validators import validate_bank_account, validate_bik, validate_inn, validate_kpp


class RecipientDetailsSerializer(serializers.ModelSerializer):
    """Сериализатор для реквизитов получателя"""

    class Meta:
        model = RecipientDetails
        fields = [
            "id",
            "full_name",
            "bank_name",
            "account_number",
            "inn",
            "kpp",
            "bik",
            "corr_account",
        ]
        read_only_fields = ["id"]

    extra_kwargs = {
        "account_number": {"validators": [validate_bank_account]},
        "inn": {"validators": [validate_inn]},
        "kpp": {"validators": [validate_kpp]},
        "bik": {"validators": [validate_bik]},
    }

    def create(self, validated_data) -> RecipientDetails:
        try:
            recipient, created = RecipientDetails.objects.get_or_create(
                inn=validated_data["inn"],
                account_number=validated_data["account_number"],
                defaults=validated_data,
            )
        except IntegrityError:
            recipient = RecipientDetails.objects.get(
                inn=validated_data["inn"], account_number=validated_data["account_number"]
            )
        return recipient

    def update(self, instance: RecipientDetails, validated_data) -> RecipientDetails:
        inn = validated_data.get("inn", instance.inn)
        account_number = validated_data.get("account_number", instance.account_number)

        if (inn != instance.inn or account_number != instance.account_number) and (
            RecipientDetails.objects.filter(inn=inn, account_number=account_number)
            .exclude(id=instance.id)
            .exists()
        ):
            raise serializers.ValidationError(
                {"inn": "Реквизиты с таким ИНН и номером счёта уже существуют."}
            )

        return super().update(instance, validated_data)


class CurrencySerializer(serializers.ModelSerializer):
    """Сериализатор для валюты"""

    class Meta:
        model = Currency
        fields = ["id", "code", "name"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        currency, created = Currency.objects.get_or_create(
            code=validated_data["code"], defaults=validated_data
        )
        return currency


class PayoutSerializer(serializers.ModelSerializer):
    """Сериализатор для заявок на выплату"""

    class Meta:
        model = Payout
        fields = [
            "id",
            "amount",
            "currency",
            "recipient_details",
            "status",
            "description",
            "created_at",
            "updated_at",
            "error_message",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "error_message"]

    def validate_status(self, value):
        # Разрешаем только: pending -> processing -> completed/failed/cancelled
        if self.instance is not None:
            old = self.instance.status
            allowed = {
                Payout.Status.PENDING: [Payout.Status.PROCESSING, Payout.Status.CANCELLED],
                Payout.Status.PROCESSING: [
                    Payout.Status.COMPLETED,
                    Payout.Status.FAILED,
                    Payout.Status.CANCELLED,
                ],
                Payout.Status.COMPLETED: [],
                Payout.Status.FAILED: [],
                Payout.Status.CANCELLED: [],
            }
            if value not in allowed.get(old, []):
                raise serializers.ValidationError(f"Нельзя перейти из {old} в {value}")
        return value

    def create(self, validated_data):
        """Создание заявки с реквизитами"""
        payout = Payout.objects.create(**validated_data)
        return payout

    def update(self, instance, validated_data):
        """Обновление заявки"""
        return super().update(instance, validated_data)

    def to_representation(self, instance: Payout):
        data = super().to_representation(instance)
        data["currency"] = {
            "id": str(instance.currency.id),
            "code": instance.currency.code,
            "name": instance.currency.name,
        }
        data["recipient_details"] = RecipientDetailsSerializer(instance.recipient_details).data
        return data
