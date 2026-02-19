import cloudinary.uploader
from cloudinary.models import CloudinaryField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import math


class ProductPurposeCategory(models.Model):
    category_name_en = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("Category name (english)"),
        error_messages={
            "unique": _("A purpose category with this name (english) already exists."),
        },
    )
    category_name_uk = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("Category name (ukrainian)"),
        error_messages={
            "unique": _("A purpose category with this name (ukranian) already exists."),
        },
    )
    image = CloudinaryField(_("image"), null=True, blank=True)

    class Meta:
        db_table = "product_purpose_category"

    def __str__(self):
        return self.category_name_en


class ProductTypeCategory(models.Model):
    type_name_en = models.CharField(
        max_length=255,
        verbose_name=_("Type name (english)"),
    )
    type_name_uk = models.CharField(
        max_length=255,
        verbose_name=_("Type name (ukrainian)"),
    )

    class Meta:
        db_table = "product_type_category"


class ProductPurposeCategoryProduct(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    purpose_category = models.ForeignKey(
        "ProductPurposeCategory", on_delete=models.CASCADE
    )

    class Meta:
        db_table = "product_purpose_category_product"
        unique_together = ("product", "purpose_category")


class Product(models.Model):
    article = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("article"),
        error_messages={
            "unique": _("Product with this article already exists."),
        },
    )
    available = models.BooleanField(default=False, verbose_name=_("available"))
    product_name_uk = models.CharField(
        max_length=250, verbose_name=_("Product name (english)")
    )
    product_name_en = models.CharField(
        max_length=250, verbose_name=_("Product name (ukrainian)")
    )
    price = models.IntegerField(
        validators=[MinValueValidator(1)], verbose_name=_("Price")
    )
    discount = models.IntegerField(verbose_name=_("Discount"))
    price_with_discount = models.IntegerField(
        editable=False, verbose_name=_("Price with discount")
    )
    description_uk = models.TextField(verbose_name=_("Description (ukrainian)"))
    description_en = models.TextField(verbose_name=_("Description (english)"))
    volume_ml = models.IntegerField(
        validators=[MinValueValidator(1)], verbose_name=_("Volume")
    )
    purpose_category = models.ManyToManyField(
        ProductPurposeCategory,
        through="ProductPurposeCategoryProduct",
        related_name="products",
    )
    type_category = models.ForeignKey(
        ProductTypeCategory,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name=_("Product type"),
    )
    is_new = models.BooleanField(default=False, verbose_name=_("New"))
    is_best_seller = models.BooleanField(default=False,
                                        verbose_name=_("Best seller"))
    ingredients = models.CharField(max_length=750, verbose_name=_("Ingredients"))
    application_uk = models.TextField(verbose_name=_("Application (ukrainian)"))
    application_en = models.TextField(verbose_name=_("Application (english)"))
    meta_tag_title_uk = models.TextField(
        default="Meta tag UK",
        verbose_name=_("Meta tag title (ukrainian)")
        )
    meta_tag_title_en = models.TextField(
        default="Meta tag EN",
        verbose_name=_("Meta tag title (english)")
        )
    meta_tag_description_uk = models.TextField(
        default="Meta tag description UK",
        verbose_name=_("Meta tag description (ukrainian)")
        )
    meta_tag_description_en = models.TextField(
        default="Meta tag description EN",
        verbose_name=_("Meta tag description (english)")
        )


    class Meta:
        db_table = "product"

    def __str__(self):
        return f"{self.product_name_en} ({self.article})"

    def get_average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return 0

        total_rating = sum([review.rating for review in reviews])
        average_rating = round(total_rating / len(reviews), 2)
        return average_rating

    def save(self, *args, **kwargs):
        self.price_with_discount = math.ceil(
            self.price - (self.price * self.discount / 100)
        )
        super().save(*args, **kwargs)
    def get_absolute_url(self):
        return f"/catalog/{self.pk}/"



class ProductImage(models.Model):
    product = models.ForeignKey(
        "Product", related_name="images", on_delete=models.CASCADE
    )
    image = CloudinaryField(_("image"))
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Order"),
        help_text=_("Order of the image in the product gallery"),
    )

    class Meta:
        db_table = "product_image"
        ordering = ["order"]

    def __str__(self):
        return f"Image for {self.product.name}"


class ProductReview(models.Model):
    product = models.ForeignKey(
        Product, related_name="reviews", on_delete=models.CASCADE
    )
    user_name = models.CharField(
        max_length=255, verbose_name=_("User Name"), default="Анонім"
    )
    rating = models.IntegerField(
        choices=[
            (1, "1 Star"),
            (2, "2 Stars"),
            (3, "3 Stars"),
            (4, "4 Stars"),
            (5, "5 Stars"),
        ],
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Rating"),
    )
    review_text = models.TextField(verbose_name=_("Review Text"), blank=True, null=True)
    date = models.DateField(auto_now_add=True, verbose_name=_("Date"))
    is_approved = models.BooleanField(default=False, verbose_name=_("Is Approved"))

    class Meta:
        db_table = "product_review"

    def __str__(self):
        return f"Review for {self.product} by {self.user_name}"

    def get_rating_stars(self):
        return [i <= self.rating for i in range(1, 6)]



class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name=_("Promo Code"))
    discount_percent = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name=_("Discount (%)")
    )
    started_at = models.DateTimeField(verbose_name=_("Started At"))
    expires_at = models.DateTimeField(verbose_name=_("Expires At"))

    class Meta:
        db_table = "promocode"

    def __str__(self):
        return self.code

    @property
    def is_active(self):
        now = timezone.now()
        return self.expires_at >= now >= self.started_at


class BannerProduct(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="banner",
        verbose_name=_("Product")
    )
    left = models.BooleanField(default=True, verbose_name=_("Left side banner"))
    image = CloudinaryField("Main image", blank=True, null=True)
    background_image = CloudinaryField("Background image", blank=True, null=True)

    class Meta:
        db_table="banner_product"

    def __str__(self):
        return f"Banner for {self.product}" 
    

def delete_cloudinary_image(sender_model):
    @receiver(post_delete, sender=sender_model)
    def _delete_cloudinary_image_handler(sender, instance, **kwargs):
        if hasattr(instance, "image") and instance.image:
            cloudinary.uploader.destroy(instance.image.public_id)
        if hasattr(instance, "background_image") and instance.background_image:
            cloudinary.uploader.destroy(instance.background_image.public_id)


delete_cloudinary_image(ProductImage)
delete_cloudinary_image(ProductPurposeCategory)
delete_cloudinary_image(BannerProduct)
      