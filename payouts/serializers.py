from rest_framework import serializers

from payouts.models import Payout, RecipientDetails
from payouts.validators import (
    validate_bank_account,
    validate_bik,
    validate_corr_account,
    validate_inn,
    validate_kpp,
)


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
        "corr_account": {"validators": [validate_corr_account]},
    }

    def create(self, validated_data) -> RecipientDetails:
        if RecipientDetails.objects.filter(inn=validated_data["inn"]).exists():
            raise serializers.ValidationError({"inn": "Получатель с таким ИНН уже существует."})

        return super().create(validated_data)

    def update(self, instance: RecipientDetails, validated_data) -> RecipientDetails:
        new_inn = validated_data.get("inn", instance.inn)

        if new_inn != instance.inn and RecipientDetails.objects.filter(inn=new_inn).exists():
            raise serializers.ValidationError({"inn": "Получатель с таким ИНН уже существует."})

        return super().update(instance, validated_data)


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

    def validate(self, data):
        # Устанавливаем статус PENDING по умолчанию при создании
        if self.instance is None:
            data["status"] = Payout.Status.PENDING
        return data

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
        data["recipient_details"] = RecipientDetailsSerializer(instance.recipient_details).data
        return data
