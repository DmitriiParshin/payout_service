import pytest

from rest_framework.test import APIClient

from payouts.models import Currency, RecipientDetails


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def currency(db):
    """Фикстура для создания тестовой валюты."""
    return Currency.objects.create(code="USD", name="Dollar")


@pytest.fixture
def recipient(db):
    """Фикстура для создания тестового получателя."""
    return RecipientDetails.objects.create(
        full_name="Test User",
        bank_name="Test Bank",
        account_number="40817810099910004312",
        inn="7707083893",
        kpp="770701001",
        bik="044525225",
        corr_account="30101810400000000225",
    )
