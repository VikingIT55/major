import pytest
from unittest import mock
from rest_framework import serializers
from contacts.serializers import ContactSerializer
from django.core.exceptions import ValidationError


def test_get_current_year():
    with mock.patch('contacts.serializers.datetime') as mock_datetime:
        mock_datetime.now.return_value.year = 2023
        serializer = ContactSerializer()
        result = serializer.get_current_year(None)
        assert result == 2023, f"Expected 2023, got {result}"


def test_validate_site_year_valid():
    with mock.patch('contacts.serializers.datetime') as mock_datetime:
        mock_datetime.now.return_value.year = 2023
        serializer = ContactSerializer()
        assert serializer.validate_site_year(2023) == 2023
        assert serializer.validate_site_year(2020) == 2020


def test_validate_site_year_invalid():
    with mock.patch('contacts.serializers.datetime') as mock_datetime:
        mock_datetime.now.return_value.year = 2023
        serializer = ContactSerializer()
        with pytest.raises(serializers.ValidationError):
            serializer.validate_site_year(2019)
        with pytest.raises(serializers.ValidationError):
            serializer.validate_site_year(mock_datetime.now.return_value.year + 1)
    

def test_validate_phone_number():
    serializer = ContactSerializer()
    data = {
        "main_phone_number": "+123456789012",
        "additional_phone_number": "+123456789012"
    }
    validated_data = serializer.validate(data)
    assert validated_data["main_phone_number"] == "+123456789012"
    assert validated_data["additional_phone_number"] == "+123456789012"


def test_validate_phone_number_invalid():
    serializer = ContactSerializer()
    with pytest.raises(serializers.ValidationError):
        serializer.validate({"main_phone_number": None})
       
    with pytest.raises(ValidationError):
        serializer.validate({"main_phone_number": "+123456789012",
                             "additional_phone_number": "12345"})
    with pytest.raises(ValidationError):
        serializer.validate({"main_phone_number": "12345"})
       
    additional_number_none = serializer.validate({"main_phone_number": "+123456789012",
                             "additional_phone_number": None})
    assert additional_number_none["additional_phone_number"] is None


def test_policy_urls_valid():
    serializer = ContactSerializer()
    data = {
        "main_phone_number": "+123456789012", 
        "offer_agreement_policy": "https://major.in.ua/",
        "exchange_and_return_policy": "https://major.in.ua/",
        "paymant_and_delivery_policy": "https://major.in.ua/"
    }
    validated_data = serializer.validate(data)
    assert validated_data["offer_agreement_policy"] == "https://major.in.ua/"
    assert validated_data["exchange_and_return_policy"] == "https://major.in.ua/"
    assert validated_data["paymant_and_delivery_policy"] == "https://major.in.ua/"


def test_policy_urls_invalid():
    data_with_invalid_url={
            "offer_agreement_policy": "major.in.ua",
            "exchange_and_return_policy": "major.in.ua",
            "paymant_and_delivery_policy": "major.in.ua"
        }
    data_with_empty_url={
            "offer_agreement_policy": "",
            "exchange_and_return_policy": "",
            "paymant_and_delivery_policy": ""
        }
    serializer = ContactSerializer(data=data_with_invalid_url)
    with pytest.raises(serializers.ValidationError):
        serializer.is_valid(raise_exception=True)
    serializer = ContactSerializer(data=data_with_empty_url)
    with pytest.raises(serializers.ValidationError):
        serializer.is_valid(raise_exception=True)
