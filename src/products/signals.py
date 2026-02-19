import requests
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.sites.models import Site
from django.conf import settings
from products.models import Product

def ping_google_custom():
    try:
        current_site = Site.objects.get_current()
        sitemap_url = f"https://{current_site.domain}/sitemap.xml"

        ping_url = "https://www.google.com/ping"
        params = {"sitemap": sitemap_url}

        requests.get(ping_url, params=params, timeout=5)

    except Exception:
        pass

@receiver(post_save, sender=Product)
def product_saved(sender, **kwargs):
    if not settings.DEBUG:
        ping_google_custom()

@receiver(post_delete, sender=Product)
def product_deleted(sender, **kwargs):
    if not settings.DEBUG:
        ping_google_custom()
