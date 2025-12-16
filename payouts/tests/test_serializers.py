from decimal import Decimal

import pytest

from payouts.models import Payout, RecipientDetails
from payouts.serializers import PayoutSerializer, RecipientDetailsSerializer


@pytest.mark.django_db
def test_recipient_serializer_create_success(valid_recipient_data):
    """Тест: успешное создание RecipientDetails."""
    serializer = RecipientDetailsSerializer(data=valid_recipient_data)
    assert serializer.is_valid(), serializer.errors
    recipient = serializer.save()
    assert RecipientDetails.objects.count() == 1
    assert recipient.inn == valid_recipient_data["inn"]


@pytest.mark.django_db
def test_recipient_serializer_create_duplicate_inn_fails(valid_recipient_data):
    """Тест: ошибка при создании получателя с существующим ИНН."""
    serializer1 = RecipientDetailsSerializer(data=valid_recipient_data)
    assert serializer1.is_valid()
    serializer1.save()

    serializer2 = RecipientDetailsSerializer(data=valid_recipient_data)
    assert not serializer2.is_valid()
    assert "inn" in serializer2.errors
    assert "уже существует" in str(serializer2.errors["inn"][0]).lower()


@pytest.mark.django_db
def test_recipient_serializer_update_same_inn_ok(valid_recipient_data):
    """Тест: обновление получателя без изменения ИНН."""
    serializer = RecipientDetailsSerializer(data=valid_recipient_data)
    assert serializer.is_valid()
    recipient = serializer.save()

    serializer = RecipientDetailsSerializer(
        instance=recipient, data={"bank_name": "ВТБ"}, partial=True
    )
    assert serializer.is_valid(), serializer.errors
    updated = serializer.save()
    assert updated.bank_name == "ВТБ"
    assert updated.inn == valid_recipient_data["inn"]


@pytest.mark.django_db
def test_recipient_serializer_update_inn_to_existing_fails(valid_recipient_data):
    """Тест: изменение ИНН на уже существующий — ошибка."""
    # Создаём первого получателя
    serializer1 = RecipientDetailsSerializer(data=valid_recipient_data)
    assert serializer1.is_valid()
    recipient1 = serializer1.save()

    # Создаём второго получателя
    data2 = {**valid_recipient_data, "inn": "7701000001", "full_name": "ООО Тюльпан"}
    serializer2 = RecipientDetailsSerializer(data=data2)
    assert serializer2.is_valid()
    recipient2 = serializer2.save()

    # Пытаемся изменить ИНН второго на ИНН первого
    serializer = RecipientDetailsSerializer(
        instance=recipient2, data={"inn": recipient1.inn}, partial=True
    )
    assert not serializer.is_valid()
    assert "inn" in serializer.errors
    assert "уже существует" in str(serializer.errors["inn"][0]).lower()


@pytest.mark.django_db
def test_recipient_serializer_update_own_inn_ok(valid_recipient_data):
    """Тест: изменение ИНН на тот же самый."""
    serializer = RecipientDetailsSerializer(data=valid_recipient_data)
    assert serializer.is_valid()
    recipient = serializer.save()

    serializer = RecipientDetailsSerializer(
        instance=recipient, data={"inn": recipient.inn, "bank_name": "Газпромбанк"}, partial=True
    )
    assert serializer.is_valid(), serializer.errors
    updated = serializer.save()
    assert updated.bank_name == "Газпромбанк"
    assert updated.inn == recipient.inn


@pytest.mark.django_db
def test_payout_serializer_create_success(valid_payout_data, recipient):
    """Тест: успешное создание выплаты."""
    serializer = PayoutSerializer(data=valid_payout_data)
    assert serializer.is_valid(), serializer.errors
    payout = serializer.save()
    assert Payout.objects.count() == 1
    assert payout.amount == Decimal("1000.00")
    assert payout.recipient_details == recipient
    assert payout.status == Payout.Status.PENDING


@pytest.mark.django_db
def test_payout_serializer_status_transition_valid(recipient):
    """Тест: корректный переход статуса."""
    payout = Payout.objects.create(
        amount=Decimal("500.00"),
        currency=Payout.Currency.RUB,
        recipient_details=recipient,
        status=Payout.Status.PENDING,
    )
    serializer = PayoutSerializer(
        instance=payout,
        data={"status": Payout.Status.PROCESSING},
        partial=True,
    )
    assert serializer.is_valid(), serializer.errors
    updated = serializer.save()
    assert updated.status == Payout.Status.PROCESSING


@pytest.mark.django_db
def test_payout_serializer_status_transition_invalid(recipient):
    """Тест: нельзя изменить статус у завершённой выплаты."""
    payout = Payout.objects.create(
        amount=Decimal("500.00"),
        currency=Payout.Currency.RUB,
        recipient_details=recipient,
        status=Payout.Status.COMPLETED,
    )
    serializer = PayoutSerializer(
        instance=payout,
        data={"status": Payout.Status.PROCESSING},
        partial=True,
    )
    assert not serializer.is_valid()
    assert "status" in serializer.errors
    assert "нельзя перейти" in str(serializer.errors["status"][0]).lower()


@pytest.mark.django_db
def test_payout_serializer_update_description_only(valid_payout_data):
    """Тест: обновление описания без изменения других полей."""
    serializer = PayoutSerializer(data=valid_payout_data)
    assert serializer.is_valid()
    payout = serializer.save()

    serializer = PayoutSerializer(
        instance=payout,
        data={"description": "Обновлённое описание"},
        partial=True,
    )
    assert serializer.is_valid(), serializer.errors
    updated = serializer.save()
    assert updated.description == "Обновлённое описание"
    assert updated.amount == payout.amount
