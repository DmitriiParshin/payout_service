from django.contrib import admin

from payouts.models import Currency, Payout, RecipientDetails


@admin.register(RecipientDetails)
class RecipientDetailsAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "bank_name", "account_number", "inn")
    list_filter = ("bank_name",)
    search_fields = ("full_name", "inn", "account_number")
    readonly_fields = ("id",)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name")
    search_fields = ("code", "name")


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ("id", "amount", "currency_code", "status_name", "created_at", "recipient_name")
    list_filter = ("status", "currency", "created_at")
    search_fields = ("id", "recipient_details__full_name", "recipient_details__inn")
    readonly_fields = ("id", "created_at", "updated_at")
    fieldsets = (
        ("Основная информация", {"fields": ("id", "amount", "currency", "status", "description")}),
        ("Реквизиты получателя", {"fields": ("recipient_details",)}),
        ("Дополнительно", {"fields": ("created_at", "updated_at", "error_message")}),
    )

    def currency_code(self, obj):
        return obj.currency.code

    currency_code.short_description = "Валюта"

    def status_name(self, obj):
        return obj.status.name

    status_name.short_description = "Статус"

    def recipient_name(self, obj):
        return obj.recipient_details.full_name

    recipient_name.short_description = "Получатель"
