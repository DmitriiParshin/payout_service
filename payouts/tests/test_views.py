from decimal import Decimal

from rest_framework.reverse import reverse

from payouts.models import Payout


def test_create_payout(api, currency, recipient, mocker):
    """Проверяем, что task вызывается"""
    mocked = mocker.patch("payouts.views.process_payout_task.delay")

    url = reverse("payout-list")
    payload = {
        "amount": "99.99",
        "currency": str(currency.id),
        "recipient_details": str(recipient.id),
        "description": "Test payout"
    }

    response = api.post(url, payload, format="json")

    assert response.status_code == 201
    mocked.assert_called_once()


def test_partial_update_allowed_fields(api, currency, recipient):
    payout = Payout.objects.create(
        amount=Decimal("50"),
        currency=currency,
        recipient_details=recipient
    )

    url = reverse("payout-detail", args=[payout.id])
    response = api.patch(url, {"description": "Updated"}, format="json")

    assert response.status_code == 200
    assert response.data["description"] == "Updated"


def test_partial_update_disallowed_fields(api, currency, recipient):
    payout = Payout.objects.create(
        amount=Decimal("50"),
        currency=currency,
        recipient_details=recipient
    )

    url = reverse("payout-detail", args=[payout.id])
    response = api.patch(url, {"amount": "100"}, format="json")

    assert response.status_code == 200
    assert response.data["amount"] == "50.00"


def test_delete_returns_object(api, currency, recipient):
    payout = Payout.objects.create(
        amount=Decimal("50"),
        currency=currency,
        recipient_details=recipient
    )

    url = reverse("payout-detail", args=[payout.id])
    response = api.delete(url)

    assert response.status_code == 200
    assert response.data["id"] == str(payout.id)
    assert not Payout.objects.filter(id=payout.id).exists()
    