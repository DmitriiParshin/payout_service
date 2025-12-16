import uuid

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class BaseModel(models.Model):
    """Абстрактная базовая модель с UUID в качестве первичного ключа."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="ID")

    class Meta:
        abstract = True


class RecipientDetails(BaseModel):
    """Модель для хранения реквизитов получателя"""

    full_name = models.CharField(max_length=255, verbose_name="Полное наименование")
    bank_name = models.CharField(max_length=255, verbose_name="Название банка")
    account_number = models.CharField(max_length=20, verbose_name="Номер счета")
    inn = models.CharField(max_length=12, unique=True, verbose_name="ИНН")
    kpp = models.CharField(max_length=9, verbose_name="КПП")
    bik = models.CharField(max_length=9, verbose_name="БИК")
    corr_account = models.CharField(max_length=20, verbose_name="Корреспондентский счет")

    class Meta:
        verbose_name = "Реквизиты получателя"
        verbose_name_plural = "Реквизиты получателей"
        ordering = ["full_name"]
        indexes = [
            models.Index(fields=["inn"]),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.inn})"


class Payout(BaseModel):
    """Модель для хранения заявок на выплаты"""

    class Currency(models.TextChoices):
        """ENUM для основных валют мира"""

        USD = "USD", "Доллар США"
        EUR = "EUR", "Евро"
        GBP = "GBP", "Фунт стерлингов"
        JPY = "JPY", "Японская иена"
        CNY = "CNY", "Китайский юань"
        CHF = "CHF", "Швейцарский франк"
        CAD = "CAD", "Канадский доллар"
        AUD = "AUD", "Австралийский доллар"
        NZD = "NZD", "Новозеландский доллар"
        RUB = "RUB", "Российский рубль"

    class Status(models.TextChoices):
        """ENUM для основных статусов заявок"""

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
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        verbose_name="Валюта",
    )
    recipient_details = models.ForeignKey(
        RecipientDetails, on_delete=models.PROTECT, verbose_name="Реквизиты получателя"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name="Статус заявки"
    )
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    error_message = models.TextField(blank=True, verbose_name="Сообщение об ошибке")

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
        return f"Заявка #{self.id} - {self.amount} {self.currency}"
