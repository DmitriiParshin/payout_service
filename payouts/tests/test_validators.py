import pytest

from rest_framework.exceptions import ValidationError

from payouts.validators import (
    validate_bank_account,
    validate_bik,
    validate_corr_account,
    validate_inn,
    validate_kpp,
)


def test_validate_bank_account_valid():
    """Тест валидного банковского счёта"""
    assert validate_bank_account("12345678901234567890") == "12345678901234567890"


def test_validate_bank_account_invalid():
    """Тест невалидного банковского счёта"""
    with pytest.raises(ValidationError):
        validate_bank_account("1234567890")  # 10 цифр
    with pytest.raises(ValidationError):
        validate_bank_account("123456789012345678901")  # 21 цифра
    with pytest.raises(ValidationError):
        validate_bank_account("1234567890123456789a")  # буква


def test_validate_inn_valid():
    """Тест валидного ИНН (10 и 12 цифр)"""
    assert validate_inn("1234567890") == "1234567890"
    assert validate_inn("123456789012") == "123456789012"


def test_validate_inn_invalid():
    """Тест невалидного ИНН"""
    with pytest.raises(ValidationError):
        validate_inn("123456789")  # 9 цифр
    with pytest.raises(ValidationError):
        validate_inn("1234567890123")  # 13 цифр
    with pytest.raises(ValidationError):
        validate_inn("123456789a")  # буква
    with pytest.raises(ValidationError):
        validate_inn("12345678901a")  # буква


def test_validate_kpp_valid():
    """Тест валидного КПП"""
    assert validate_kpp("123456789") == "123456789"


def test_validate_kpp_invalid():
    """Тест невалидного КПП"""
    with pytest.raises(ValidationError):
        validate_kpp("12345678")  # 8 цифр
    with pytest.raises(ValidationError):
        validate_kpp("1234567890")  # 10 цифр
    with pytest.raises(ValidationError):
        validate_kpp("12345678a")  # буква


def test_validate_bik_valid():
    """Тест валидного БИКа"""
    assert validate_bik("123456789") == "123456789"


def test_validate_bik_invalid():
    """Тест невалидного БИКа"""
    with pytest.raises(ValidationError):
        validate_bik("12345678")  # 8 цифр
    with pytest.raises(ValidationError):
        validate_bik("1234567890")  # 10 цифр
    with pytest.raises(ValidationError):
        validate_bik("12345678a")  # буква


def test_validate_corr_account_valid():
    """Тест валидного корреспондентского счёта (20 цифр, начинается с '301')"""
    assert validate_corr_account("30145678901234567890") == "30145678901234567890"


def test_validate_corr_account_invalid_length():
    """Тест длины корреспондентского счёта"""
    with pytest.raises(ValidationError):
        validate_corr_account("3014567890123456789")  # 19 цифр
    with pytest.raises(ValidationError):
        validate_corr_account("301456789012345678901")  # 21 цифра


def test_validate_corr_account_invalid_start():
    """Тест, что счёт начинается с '301'"""
    with pytest.raises(ValidationError):
        validate_corr_account("10145678901234567890")  # не с 301


def test_validate_corr_account_invalid_chars():
    """Тест наличия нецифровых символов"""
    with pytest.raises(ValidationError):
        validate_corr_account("3014567890123456789a")
