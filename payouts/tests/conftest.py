from decimal import Decimal

import pytest

from rest_framework.test import APIClient

from payouts.models import Payout, RecipientDetails


@pytest.fixture
def api():
    """Фикстура для API клиента."""
    return APIClient()


@pytest.fixture
def recipient(db):
    """Фикстура для создания тестового получателя."""
    return RecipientDetails.objects.create(
        full_name="ООО Ромашка",
        bank_name="Сбербанк",
        account_number="40817810900000000001",
        inn="7701000000",
        kpp="770101001",
        bik="044525225",
        corr_account="30101810400000000225",
    )


@pytest.fixture
def valid_recipient_data():
    """Валидные данные для RecipientDetails."""
    return {
        "full_name": "ООО Ромашка",
        "bank_name": "Сбербанк",
        "account_number": "40817810900000000001",
        "inn": "7701001001",
        "kpp": "770101001",
        "bik": "044525225",
        "corr_account": "30101810400000000225",
    }


@pytest.fixture
def payout(db, recipient):
    """Фикстура для создания выплаты."""
    return Payout.objects.create(
        amount=Decimal("1000.00"),
        currency=Payout.Currency.RUB,
        recipient_details=recipient,
        description="Выплата за поставку",
    )


@pytest.fixture
def valid_payout_data(recipient):
    """Валидные данные для Payout."""
    return {
        "amount": "1000.00",
        "currency": "RUB",
        "recipient_details": recipient.id,
        "description": "Выплата за поставку",
    }
