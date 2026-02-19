from django.db import models
from django.core.exceptions import ValidationError


class Contact(models.Model):

    telegram = models.CharField(
        max_length=255,
        verbose_name="Telegram handle",
    )
    instagram = models.CharField(
        max_length=255,
        verbose_name="Instagram handle",
    )
    email = models.EmailField(
        max_length=255,
        verbose_name="Email address",
    )
    main_phone_number = models.CharField(
        max_length=13,
        verbose_name="Main phone number",
    )
    additional_phone_number = models.CharField(
        max_length=13,
        blank=True,
        null=True,
        verbose_name="Additional phone number",
    )
    work_schedule_weekdays = models.CharField(
        max_length=255,
        verbose_name="Work schedule on weekdays",
    )
    work_schedule_weekends = models.CharField(
        max_length=255,
        verbose_name="Work schedule on weekends",
    )
    offer_agreement_policy = models.URLField(
        max_length=255,
        verbose_name="Offer agreement URL",
    )
    exchange_and_return_policy = models.URLField(
        max_length=255,
        verbose_name="Exchange and return policy URL",
    )
    paymant_and_delivery_policy = models.URLField(
        max_length=255,
        verbose_name="Payment and delivery information URL",
    )
    
    def clean(self):
        if Contact.objects.exists() and not self.pk:
            raise ValidationError("Only one contact instance is allowed.")
        return super().clean()
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        db_table = "contact"

    def __str__(self):
        return f"Contact {self.id} - {self.telegram or self.email or self.main_phone_number}"

