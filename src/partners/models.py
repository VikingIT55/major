from django.db import models


class PartnerLocation(models.Model):
    name_uk = models.CharField(max_length=255, verbose_name='Name (ukr)')
    name_en = models.CharField(max_length=255, verbose_name='Name (eng)')
    addres_uk = models.TextField(verbose_name='Address (ukr)')
    addres_en = models.TextField(verbose_name='Address (eng)')
    work_schedule_weekdays = models.CharField(max_length=255, verbose_name='Work schedule weekdays')
    work_schedule_weekends = models.CharField(max_length=255, verbose_name='Work schedule weekends')
    google_maps_link = models.URLField(max_length=500, verbose_name='Google Maps link')
    longitude = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Longitude (x)')
    latitude = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Latitude (y)')

    class Meta:
        db_table = 'partner_location'

    def __str__(self):
        return self.name_en
       