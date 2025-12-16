from decimal import Decimal

import pytest

from django.core.exceptions import ValidationError
from django.db import IntegrityError

from payouts.models import Payout, RecipientDetails


@pytest.mark.django_db
def test_recipient_details_creation(recipient):
    """Тест создания экземпляра RecipientDetails."""
    assert recipient.full_name == "ООО Ромашка"
    assert recipient.inn == "7701000000"
    assert recipient.account_number == "40817810900000000001"
    assert str(recipient) == "ООО Ромашка (7701000000)"


@pytest.mark.django_db
def test_recipient_details_unique_constraint(recipient):
    """Тест уникального ограничения по INN."""
    with pytest.raises(IntegrityError):
        RecipientDetails.objects.create(
            full_name="ООО Ромашка 2",
            bank_name="ВТБ",
            account_number="40817810900000000001",
            inn="7701000000",  # такой же ИНН
            kpp="770101002",
            bik="044525226",
            corr_account="30101810400000000226",
        )


@pytest.mark.django_db
def test_payout_creation(payout):
    """Тест создания выплаты."""
    assert payout.amount == Decimal("1000.00")
    assert payout.currency == "RUB"
    assert payout.status == Payout.Status.PENDING
    assert "Заявка #" in str(payout)
    assert "1000.00 RUB" in str(payout)


@pytest.mark.django_db
def test_payout_amount_validation(recipient):
    """Тест валидации суммы (меньше 0.01)."""
    payout = Payout(
        amount=Decimal("0.00"),
        currency=Payout.Currency.RUB,
        recipient_details=recipient,
    )
    with pytest.raises(ValidationError):
        payout.full_clean()


@pytest.mark.django_db
def test_payout_status_default(payout):
    """Тест: статус по умолчанию — PENDING."""
    assert payout.status == Payout.Status.PENDING


@pytest.mark.django_db
def test_payout_currency_choices(recipient):
    """Тест: только разрешённые валюты."""
    payout = Payout(
        amount=Decimal("100.00"),
        currency="XYZ",
        recipient_details=recipient,
    )
    with pytest.raises(ValidationError):
        payout.full_clean()


@pytest.mark.django_db
def test_payout_str_representation(payout):
    """Тест строкового представления Payout."""
    assert str(payout) == f"Заявка #{payout.id} - 1000.00 RUB"
