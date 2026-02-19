import cloudinary.uploader
from django.db import models
from django.dispatch import receiver
from cloudinary.models import CloudinaryField
from django.db.models.signals import post_delete


class Blog(models.Model):
    content = models.TextField(verbose_name="Content")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")

    class Meta:
        db_table = "blog"


class BlogImage(models.Model):
    image = CloudinaryField("image")
    
    class Meta:
        db_table = "blog_image"

    

@receiver(post_delete, sender=BlogImage)
def delete_cloudinary_image_blog(sender, instance, **kwargs):
    if instance.image:
        cloudinary.uploader.destroy(instance.image.public_id)
