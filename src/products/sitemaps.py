from django.contrib.sitemaps import Sitemap
from products.models import Product

class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0

    def items(self):
        return Product.objects.all()
