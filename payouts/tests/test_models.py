from decimal import Decimal

import pytest

from payouts.models import Payout, RecipientDetails


@pytest.mark.django_db
def test_currency_str(currency):
    assert str(currency) == "USD - Dollar"


@pytest.mark.django_db
def test_recipient_unique_constraint(recipient):
    with pytest.raises(Exception):
        RecipientDetails.objects.create(
            full_name="Another",
            bank_name="Bank",
            account_number=recipient.account_number,
            inn=recipient.inn,
            kpp="123456789",
            bik="111222333",
            corr_account="1111222233334444",
        )


@pytest.mark.django_db
def test_payout_str(currency, recipient):
    payout = Payout.objects.create(
        amount=Decimal("100.50"), currency=currency, recipient_details=recipient
    )
    assert "100.50" in str(payout)
    assert currency.code in str(payout)
