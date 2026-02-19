from rest_framework.permissions import SAFE_METHODS, BasePermission
from users.constants import Role


class ContactPermission(BasePermission):
    """Custom permission for ContactViewSet.
    - Admin full access.
    - Manager can GET.
    - User can GET.
    """
    def has_permission(self, request, view):
        user = request.user
        if user.is_anonymous:
            return request.method in SAFE_METHODS
        if user.role == Role.ADMIN:
            return True
        elif user.role == Role.MANAGER:
            return request.method in SAFE_METHODS
        elif user.role == Role.USER:
            return request.method in SAFE_METHODS
        return False