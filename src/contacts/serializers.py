from rest_framework import serializers
from django.core.validators import RegexValidator
from datetime import datetime

from contacts.models import Contact


phone_validator = RegexValidator(
    regex=r'^\+\d{12}$',
    message='Phone number must be in the format: +123456789012',
)

class ContactSerializer(serializers.ModelSerializer):
    current_year = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = [
            "id",
            "telegram",
            "instagram",
            "email",
            "main_phone_number",
            "additional_phone_number",
            "work_schedule_weekdays",
            "work_schedule_weekends",
            "offer_agreement_policy",
            "exchange_and_return_policy",
            "paymant_and_delivery_policy",
            "current_year",
        ]

    def get_current_year(self, obj):
        return datetime.now().year
    
    def validate_site_year(self, value):
        current_year = datetime.now().year
        if value < 2020 or value > current_year:
            raise serializers.ValidationError(
                f"Site year must be between 2020 and {current_year}."
            )
        return value
    
    def validate(self, data):
        main = data.get("main_phone_number")
        if not main:
            raise serializers.ValidationError({
                "main_phone_number": "Main phone number is required."
            })
        phone_validator(main)

        additional = data.get('additional_phone_number')
        if additional:
            phone_validator(additional)
        
        if not self.instance and Contact.objects.exists():
            raise serializers.ValidationError("Only one contact instance is allowed.")

        return data


