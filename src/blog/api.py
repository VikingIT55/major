from rest_framework import viewsets, status
from rest_framework.response import Response

from blog.models import Blog, BlogImage
from blog.serializers import BlogSerializer, BlogImageSerializer
from products.permissions import RoleIsAdmin, RoleIsManager, RoleIsUser




class BlogViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing blog posts.
    """
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [RoleIsAdmin | RoleIsManager | RoleIsUser]

class BlogImageViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing blog images.
    """
    queryset = BlogImage.objects.all()
    serializer_class = BlogImageSerializer
    permission_classes = [RoleIsAdmin | RoleIsManager | RoleIsUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "detail": "Image uploaded successfully.",
                "image": getattr(serializer, "cloudinary_responses", [])
            },
            status=status.HTTP_201_CREATED
        )

