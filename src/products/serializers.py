import cloudinary.uploader
from django.conf import settings
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from PIL import Image
from rest_framework import serializers
from users.constants import Role

from products.models import (BannerProduct, Product, ProductImage,
                             ProductPurposeCategory, ProductReview,
                             ProductTypeCategory, PromoCode)


class ImageValidator:
    def __init__(self, max_size_mb=1, max_width=1920, max_height=1080, allowed_extensions=None):
        self.max_size_mb = max_size_mb
        self.max_width = max_width
        self.max_height = max_height
        self.allowed_extensions = allowed_extensions or (".jpg", ".jpeg", ".png", ".webp")

    def __call__(self, image):
        if not image.name.lower().endswith(self.allowed_extensions):
            raise serializers.ValidationError(_(f"Only file types {self.allowed_extensions} are allowed."))

        if image.size > self.max_size_mb * 1024 * 1024:
            raise serializers.ValidationError(_(f"File size must be <= {self.max_size_mb}MB."))

        image.file.seek(0)
        img = Image.open(image.file)
        width, height = img.size
        if width > self.max_width or height > self.max_height:
            raise serializers.ValidationError(
                _(f"Image resolution must be <= {self.max_width}x{self.max_height}px.")
            )


class ProductPurposeCategorySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    upload_image = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = ProductPurposeCategory
        fields = ["id", "category_name_uk", "category_name_en", "image", "upload_image"]

    def validate_upload_image(self, image):
        validator = ImageValidator()
        validator(image)
        return image

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request", None)
        lang_code = get_language()
        representation["name"] = (
            instance.category_name_uk
            if lang_code == "uk"
            else instance.category_name_en
        )
        if (
            request
            and request.user.is_authenticated
            and request.user.role in [Role.ADMIN, Role.MANAGER]
        ):
            pass
        else:
            representation.pop("category_name_uk", None)
            representation.pop("category_name_en", None)
        if instance.image:
            representation["image"] = (
                f"https://res.cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}/image/upload/{instance.image}"
            )
        return representation

    def create(self, validated_data):
        image = validated_data.pop("image", None)
        if ProductPurposeCategory.objects.filter(
            category_name_en__iexact=validated_data["category_name_en"]
        ).exists():
            raise serializers.ValidationError(
                {
                    "category_name_en": _(
                        "A purpose category with this English name already exists (different case)."
                    )
                }
            )
        if ProductPurposeCategory.objects.filter(
            category_name_uk__iexact=validated_data["category_name_uk"]
        ).exists():
            raise serializers.ValidationError(
                {
                    "category_name_uk": _(
                        "A purpose category with this Ukrainian name already exists (different case)."
                    )
                }
            )
        instance = ProductPurposeCategory.objects.create(**validated_data)
        if image:
            instance.image = image
            instance.save()
        return instance

    def update(self, instance, validated_data):
        new_image = validated_data.pop("upload_image", None)
        if new_image and instance.image:
            try:
                public_id = (
                    instance.image.public_id
                    if hasattr(instance.image, "public_id")
                    else instance.image.name.split(".")[0]
                )
                cloudinary.uploader.destroy(public_id)
            except Exception as e:
                print(f"Cloudinary delete error: {e}")

            instance.image = new_image
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ProductTypeCategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ProductTypeCategory
        fields = ["id", "type_name_uk", "type_name_en", "product_count"]
    
    
    def validate(self, data):
        type_name_en = data.get('type_name_en')
        if type_name_en:
            queryset = ProductTypeCategory.objects.filter(
                type_name_en__iexact=type_name_en
            )
            if self.instance:  
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError({
                    'type_name_en': _("A type category with this english name already exists (case insensitive).")
                })

        type_name_uk = data.get('type_name_uk')
        if type_name_uk:
            queryset = ProductTypeCategory.objects.filter(
                type_name_uk__iexact=type_name_uk
            )
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError({
                    'type_name_uk': _("A type category with this ukrainian name already exists (case insensitive).")
                })
        return data

    def get_product_count(self, obj):
        return Product.objects.filter(type_category=obj).count()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request", None)
        lang_code = get_language()
        representation["name"] = (
            instance.type_name_uk if lang_code == "uk" else instance.type_name_en
        )
        if (
            request
            and request.user.is_authenticated
            and request.user.role in [Role.ADMIN, Role.MANAGER]
        ):
            pass
        else:
            representation.pop("type_name_uk", None)
            representation.pop("type_name_en", None)
        return representation


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["id", "image", "order"]

    def get_image(self, obj):
        return f"https://res.cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}/image/upload/{obj.image}"


class ProductReviewSerializer(serializers.ModelSerializer):
    stars = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProductReview
        fields = [
            "id",
            "rating",
            "product_name",
            "review_text",
            "user_name",
            "date",
            "is_approved",
            "product_id",
            "stars",
        ]
        read_only_fields = ["is_approved", "product_id"]

    def validate_user_name(self, value):
        if not value or value.strip() == "":
            return "Анонім"
        return value

    def create(self, validated_data):
        review = ProductReview.objects.create(**validated_data)
        return review

    def get_stars(self, obj):
        return obj.get_rating_stars()

    def get_product_name(self, obj):
        lang_code = get_language()
        if lang_code == "uk":
            return obj.product.product_name_uk
        return obj.product.product_name_en


class ProductSerializer(serializers.ModelSerializer):
    purpose_category = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ProductPurposeCategory.objects.all(),
        label=_("Purpose category"),
    )
    images = ProductImageSerializer(many=True, read_only=True)
    upload_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        label=_("Upload Images"),
    )
    remove_images = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        label=_("Remove Image IDs"),
    )
    update_images_order = serializers.ListField(
    child=serializers.DictField(),
    write_only=True,
    required=False,
    )
    reviews = ProductReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField(read_only=True)
    is_discount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "article",
            "available",
            "product_name_uk",
            "product_name_en",
            "price",
            "discount",
            "is_discount",
            "price_with_discount",
            "description_uk",
            "description_en",
            "volume_ml",
            "images",
            "upload_images",
            "remove_images",
            "update_images_order",
            "purpose_category",
            "type_category",
            "is_new",
            "is_best_seller",
            "ingredients",
            "application_uk",
            "application_en",
            "reviews",
            "average_rating",
            "meta_tag_title_uk",
            "meta_tag_title_en",
            "meta_tag_description_uk",
            "meta_tag_description_en",
        ]

    def validate_upload_images(self, images):
        validator = ImageValidator()
        errors = []
        for image in images:
            try:
                validator(image)
            except serializers.ValidationError as e:
                errors.append([image.name, str(e)])
        if errors:
            raise serializers.ValidationError(errors)
        return images
    
    def validate_update_images_order(self, value):
        for image in value:
            if image.get("order", 0) > 4:
                raise serializers.ValidationError(
                    _("Maximum image order value from 0 to 4 inclusive.")
                )
        return value

    def create(self, validated_data):
        purpose_categories = validated_data.pop("purpose_category", [])
        images_data = validated_data.pop("upload_images", [])
        product = Product.objects.create(**validated_data)
        product.purpose_category.set(purpose_categories)
        max_images = 5
        number_of_images = len(images_data)
        if number_of_images > max_images:
            raise serializers.ValidationError(
                {"upload_images": _(f"You can't add more than {max_images} images.")}
            )
        for image_data in images_data:
            ProductImage.objects.create(product=product, image=image_data)
        return product

    def update(self, instance, validated_data):
        remove_image_ids = validated_data.pop("remove_images", [])
        ProductImage.objects.filter(id__in=remove_image_ids, product=instance).delete()
        images_data = validated_data.pop("upload_images", [])
        max_images = 10
        product = Product.objects.get(id=instance.id)
        existing_count = product.images.count()
        new_count = len(images_data)
        if existing_count + new_count > max_images:
            raise serializers.ValidationError(
                {"upload_images":
                _(f"You can't add more than {max_images} images. Right now you have {existing_count} \
                images and you are trying to add {new_count} new ones.")}
            )
        for image_data in images_data:
            ProductImage.objects.create(product=instance, image=image_data)

        order_data = validated_data.pop("update_images_order", [])
        for image_info in order_data:
            image_id = image_info.get("id")
            new_order = image_info.get("order")
            ProductImage.objects.filter(id=image_id, product=instance).update(order=new_order)

        return super().update(instance, validated_data)

    def get_average_rating(self, obj):
        return obj.get_average_rating()

    def get_is_discount(self, obj):
        return obj.discount > 0

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request", None)
        approved_reviews = [
            review for review in representation["reviews"] if review["is_approved"]
        ]
        lang_code = get_language()
        if lang_code == "uk":
            representation["name"] = instance.product_name_uk
            representation["description"] = instance.description_uk
            representation["application"] = instance.application_uk
            representation["meta_tag_title"] = instance.meta_tag_title_uk
            representation["meta_tag_description"] = instance.meta_tag_description_uk
        else:
            representation["name"] = instance.product_name_en
            representation["description"] = instance.description_en
            representation["application"] = instance.application_en
            representation["meta_tag_title"] = instance.meta_tag_title_en
            representation["meta_tag_description"] = instance.meta_tag_description_en

        if (
            request
            and request.user.is_authenticated
            and request.user.role in [Role.ADMIN, Role.MANAGER]
        ):
            pass
        else:
            representation.pop("product_name_uk", None)
            representation.pop("product_name_en", None)
            representation.pop("description_uk", None)
            representation.pop("description_en", None)
            representation.pop("application_uk", None)
            representation.pop("application_en", None)
            representation.pop("meta_tag_title_uk", None)
            representation.pop("meta_tag_title_en", None)
            representation.pop("meta_tag_description_uk", None)
            representation.pop("meta_tag_description_en", None)

        approved_reviews = [
            review for review in representation["reviews"] if review["is_approved"]
        ]
        representation["reviews"] = approved_reviews
        return representation


class PromoCodeSerializer(serializers.ModelSerializer):
    is_active = serializers.ReadOnlyField()

    class Meta:
        model = PromoCode
        fields = ['id', 'code', 'discount_percent', 'started_at', 'expires_at', 'is_active']

    def get_is_active(self, obj):
        return obj.is_active
    
    def validate(self, data):
        started_at = data.get("started_at") or (self.instance.started_at if self.instance else None)
        expires_at = data.get("expires_at") or (self.instance.expires_at if self.instance else None)

        if started_at > expires_at:
            raise serializers.ValidationError(
                {"started_at": _("Start date cannot be later than expiration date.")}
            )
        return data
    

class PromoCodeValidateSerializer(serializers.Serializer):
    code = serializers.CharField()


class PromoCodeValidateResponseSerializer(serializers.Serializer):
    discount_percent = serializers.IntegerField()
    

class BannerProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True
    )
    image = serializers.ImageField(write_only=True, required=False)
    image_url = serializers.SerializerMethodField(read_only=True)
    background_image = serializers.ImageField(write_only=True, required=True)
    background_image_url = serializers.SerializerMethodField()

    class Meta:
        model = BannerProduct
        fields = [
                  "id", 
                  "product", 
                  "product_id", 
                  "left", 
                  "image", 
                  "image_url", 
                  "background_image", 
                  "background_image_url"
                  ]
        
    def validate_image(self, image):
        self._validate_file(image, field_name="image")
        return image

    def validate_background_image(self, image):
        self._validate_file(image, field_name="background_image")
        return image

    def _validate_file(self, image, field_name):
        allowed_extensions = (".jpg", ".jpeg", ".png", ".webp")
        max_size_mb = 10

        if not image.name.lower().endswith(allowed_extensions):
            raise serializers.ValidationError(
                _(f"Only file types {allowed_extensions} are allowed.")
            )

        if image.size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError(
                _(f"File size must be <= {max_size_mb}MB.")
            )

    def get_image_url(self, obj):
        if obj.image:
            return f"https://res.cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}/image/upload/{obj.image}"
        return None

    def get_background_image_url(self, obj):
        if obj.background_image:
            return f"https://res.cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}/image/upload/{obj.background_image}"
        return None
    
    def create(self, validated_data):
        product = validated_data.pop("product_id") 
        if BannerProduct.objects.filter(product=product).exists():
            raise serializers.ValidationError({
                "product_id": _("Banner for this product already exists.")
            })
        validated_data["product"] = product
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        new_product = validated_data.pop("product_id", None)

        if new_product:
            if BannerProduct.objects.filter(product=new_product).exclude(id=instance.id).exists():
                raise serializers.ValidationError({"product_id": "This product is already linked to another banner."})
            instance.product = new_product

        new_image = validated_data.pop("image", None)
        new_background_image = validated_data.pop("background_image", None)

        if new_image and instance.image:
            try:
                public_id = instance.image.public_id if hasattr(instance.image, "public_id") else instance.image.name.split(".")[0]
                cloudinary.uploader.destroy(public_id)
            except Exception as e:
                print(f"Cloudinary deletion error: {e}")

            instance.image = new_image
        
        if new_background_image and instance.background_image:
            try:
                cloudinary.uploader.destroy(instance.background_image.public_id)
            except Exception as e:
                print(f"Cloudinary background delete error: {e}")
            instance.background_image = new_background_image

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
    