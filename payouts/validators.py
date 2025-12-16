import re

from typing import Any

from rest_framework import serializers


def validate_bank_account(value: Any):
    """Валидация банковского счета (20 цифр)"""
    if not re.match(r"^\d{20}$", str(value)):
        raise serializers.ValidationError("Номер счета должен содержать 20 цифр")
    return value


def validate_inn(value: Any):
    """Валидация ИНН (10 или 12 цифр)"""
    value = str(value)
    if len(value) not in (10, 12) or not value.isdigit():
        raise serializers.ValidationError("ИНН должен содержать 10 или 12 цифр")
    return value


def validate_kpp(value: Any):
    """Валидация КПП (9 цифр)"""
    if not re.match(r"^\d{9}$", str(value)):
        raise serializers.ValidationError("КПП должен содержать 9 цифр")
    return value


def validate_bik(value: Any):
    """Валидация БИК (9 цифр)"""
    if not re.match(r"^\d{9}$", str(value)):
        raise serializers.ValidationError("БИК должен содержать 9 цифр")
    return value


def validate_corr_account(value: Any):
    """Валидация корреспондентского счета (20 цифр и начинается с '301')"""
    value_str = str(value)
    if not re.match(r"^\d{20}$", value_str):
        raise serializers.ValidationError("Номер счета должен содержать 20 цифр")
    if not value_str.startswith("301"):
        raise serializers.ValidationError(
            "Номер корреспондентского счета должен начинаться с '301'"
        )
    return value
