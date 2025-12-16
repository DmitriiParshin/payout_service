from decimal import Decimal

import pytest

from rest_framework.reverse import reverse

from payouts.models import Payout


@pytest.mark.django_db
def test_create_payout_calls_task(api, recipient, mocker):
    """Тест: при создании выплаты вызывается Celery-задача."""
    mocked = mocker.patch("payouts.views.process_payout_task.delay")

    url = reverse("payout-list")
    payload = {
        "amount": "99.99",
        "currency": Payout.Currency.RUB,
        "recipient_details": str(recipient.id),
        "description": "Test payout",
    }

    response = api.post(url, payload, format="json")

    assert response.status_code == 201
    assert response.data["amount"] == "99.99"
    assert response.data["status"] == Payout.Status.PENDING

    payout_id = response.data["id"]
    mocked.assert_called_once_with(payout_id)


@pytest.mark.django_db
def test_partial_update_allowed_fields(api, payout):
    """Тест: разрешённые поля можно обновить."""
    url = reverse("payout-detail", args=[payout.id])
    payload = {"description": "Updated description", "status": Payout.Status.PROCESSING}

    response = api.patch(url, payload, format="json")

    assert response.status_code == 200
    assert response.data["description"] == "Updated description"
    assert response.data["status"] == Payout.Status.PROCESSING

    payout.refresh_from_db()
    assert payout.description == "Updated description"
    assert payout.status == Payout.Status.PROCESSING


@pytest.mark.django_db
def test_partial_update_disallowed_fields_ignored(api, payout):
    """Тест: запрещённые поля (например, amount) игнорируются при обновлении."""
    url = reverse("payout-detail", args=[payout.id])
    payload = {"amount": "2000.00", "currency": "USD"}

    response = api.patch(url, payload, format="json")

    assert response.status_code == 200
    assert response.data["amount"] == "1000.00"  # не изменилось
    assert response.data["currency"] == "RUB"  # не изменилось

    payout.refresh_from_db()
    assert payout.amount == Decimal("1000.00")
    assert payout.currency == Payout.Currency.RUB


@pytest.mark.django_db
def test_delete_returns_serialized_object(api, payout):
    """Тест: при удалении возвращается сериализованный объект."""
    url = reverse("payout-detail", args=[payout.id])
    response = api.delete(url)

    assert response.status_code == 200
    assert response.data["id"] == str(payout.id)
    assert response.data["amount"] == "1000.00"
    assert not Payout.objects.filter(id=payout.id).exists()


@pytest.mark.django_db
def test_create_payout_invalid_recipient(api):
    """Тест: ошибка при создании с несуществующим получателем."""
    url = reverse("payout-list")
    payload = {
        "amount": "100.00",
        "currency": "RUB",
        "recipient_details": "123e4567-e89b-12d3-a456-426614174000",
        "description": "Invalid recipient",
    }

    response = api.post(url, payload, format="json")

    assert response.status_code == 400
    assert "recipient_details" in response.data
    assert "Недопустимый первичный ключ" in str(response.data["recipient_details"][0])


@pytest.mark.django_db
def test_create_payout_missing_required_fields(api):
    """Тест: ошибка при отсутствии обязательного поля - amount."""
    url = reverse("payout-list")
    payload = {}

    response = api.post(url, payload, format="json")

    assert response.status_code == 400
    assert "recipient_details" in response.data
    assert "amount" in response.data
