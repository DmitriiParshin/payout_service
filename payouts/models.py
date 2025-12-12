import uuid

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class BaseModel(models.Model):
    """
    Абстрактная базовая модель с UUID в качестве первичного ключа.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="ID")

    class Meta:
        abstract = True


class Currency(BaseModel):
    """Модель для хранения различных валют"""

    code = models.CharField(max_length=3, unique=True, verbose_name="Код валюты")
    name = models.CharField(max_length=100, verbose_name="Название валюты")

    class Meta:
        verbose_name = "Валюта"
        verbose_name_plural = "Валюты"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class RecipientDetails(BaseModel):
    """Модель для хранения реквизитов получателя"""

    full_name = models.CharField(max_length=255, verbose_name="Полное наименование")
    bank_name = models.CharField(max_length=255, verbose_name="Название банка")
    account_number = models.CharField(max_length=20, verbose_name="Номер счета")
    inn = models.CharField(max_length=12, verbose_name="ИНН")
    kpp = models.CharField(max_length=9, verbose_name="КПП")
    bik = models.CharField(max_length=9, verbose_name="БИК")
    corr_account = models.CharField(max_length=20, verbose_name="Корреспондентский счет")

    class Meta:
        verbose_name = "Реквизиты получателя"
        verbose_name_plural = "Реквизиты получателей"
        ordering = ["full_name"]
        indexes = [
            models.Index(fields=["inn"]),
            models.Index(fields=["bik"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["inn", "account_number"], name="uniq_inn_account")
        ]

    def __str__(self):
        return f"{self.full_name} ({self.account_number})"


class Payout(BaseModel):
    """Модель для хранения заявок на выплаты"""

    class Status(models.TextChoices):
        PENDING = "pending", "Ожидает обработки"
        PROCESSING = "processing", "В обработке"
        COMPLETED = "completed", "Выполнена"
        FAILED = "failed", "Ошибка"
        CANCELLED = "cancelled", "Отменена"

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Сумма выплаты",
    )
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, verbose_name="Валюта")
    recipient_details = models.ForeignKey(
        RecipientDetails, on_delete=models.PROTECT, verbose_name="Реквизиты получателя"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name="Статус заявки"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    error_message = models.TextField(blank=True, null=True, verbose_name="Сообщение об ошибке")

    class Meta:
        verbose_name = "Заявка на выплату"
        verbose_name_plural = "Заявки на выплату"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["currency"]),
        ]

    def __str__(self):
        return f"Заявка #{self.id} - {self.amount} {self.currency.code}"
