from django.conf import settings
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
import cloudinary.uploader

from blog.models import Blog, BlogImage
from products.serializers import ImageValidator


class BlogImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    upload_image = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        label="Upload Image",
    )

    class Meta:
        model = BlogImage
        fields = [
            "id",
            "image",
            "upload_image"
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
    
    def create(self, validated_data):
        self.cloudinary_responses = [] 
        images_data = validated_data.pop("upload_image", [])
        max_images = 10

        if len(images_data) > max_images:
            raise serializers.ValidationError(
                {
                    "upload_image": _(
                        f"You can't add more than {max_images} images."
                    )
                }
            )
        if images_data:
            for image_data in images_data:
                obj = BlogImage.objects.create(image=image_data)
                url = obj.image.build_url() if hasattr(obj.image, "build_url") else None
                if url:
                    self.cloudinary_responses.append({
                        "id": obj.id,
                        "url": url,
                    })
        else:
            raise serializers.ValidationError({"upload_image": _("Please upload an image.")})        
        return obj

    def update(self, instance, validated_data):
        new_images = validated_data.pop("upload_image", [])
        if not new_images:
            raise serializers.ValidationError({"upload_image": _("Please upload a new image.")})
        elif len(new_images) > 1:
            raise serializers.ValidationError({"upload_image": _("You can only upload one image at a time.")})
        if instance.image and hasattr(instance.image, 'public_id'):
            try:
                cloudinary.uploader.destroy(instance.image.public_id)
            except Exception as e:
                print(f"Cloudinary delete error: {e}")

        instance.image = new_images[0]
        instance.save()

        return instance

    def get_image(self, obj):
        return f"https://res.cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}/image/upload/{obj.image}"


class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = [
            "id",
            "content",
            "created_at",
        ]