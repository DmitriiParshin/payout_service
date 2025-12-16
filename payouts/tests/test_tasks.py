from decimal import Decimal
from unittest.mock import patch

import pytest

from payouts.models import Payout
from payouts.tasks import process_payout_logic


@pytest.mark.django_db
def test_process_payout_logic_success(recipient):
    """Проверяем успешную обработку"""

    payout = Payout.objects.create(amount=Decimal("50"), recipient_details=recipient)

    with patch("random.random", return_value=0.5), patch("time.sleep", return_value=None):
        result = process_payout_logic(str(payout.id))

        payout.refresh_from_db()
        assert payout.status == Payout.Status.COMPLETED
        assert result["status"] == "completed"


def test_process_payout_logic_random_error(recipient):
    """Проверяем ошибку при банковской операции"""

    payout = Payout.objects.create(amount=Decimal("50"), recipient_details=recipient)

    with patch("random.random", return_value=0.05), patch("time.sleep", return_value=None):
        # Ожидаем исключение
        with pytest.raises(Exception, match="Ошибка при выполнении банковской операции"):
            process_payout_logic(str(payout.id))

        payout.refresh_from_db()
        # Заявка должна остаться в PROCESSING, так как исключение было выброшено
        assert payout.status == Payout.Status.PROCESSING


def test_process_payout_logic_validation_failed(recipient):
    """Проверяем провал валидации"""

    payout = Payout.objects.create(
        amount=Decimal("0"),  # Невалидная сумма
        currency=Payout.Currency.RUB,
        recipient_details=recipient,
    )

    with patch("time.sleep", return_value=None):
        result = process_payout_logic(str(payout.id))

        payout.refresh_from_db()
        assert payout.status == Payout.Status.FAILED
        assert result["status"] == "failed"
        assert "Проверка данных" in payout.error_message
