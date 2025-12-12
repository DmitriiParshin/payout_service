from decimal import Decimal

from rest_framework.reverse import reverse

from payouts.models import Payout


def test_payout_status_validation(api, currency, recipient):
    payout = Payout.objects.create(
        amount=Decimal("50"),
        currency=currency,
        recipient_details=recipient,
        status=Payout.Status.COMPLETED
    )

    url = reverse("payout-detail", args=[payout.id])
    response = api.patch(url, {"status": "processing"}, format="json")

    assert response.status_code == 400
    assert "Нельзя перейти" in str(response.data)
    