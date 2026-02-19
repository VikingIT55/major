from django.contrib.auth.models import AnonymousUser
from rest_framework.permissions import SAFE_METHODS, BasePermission

from users.constants import Role


class BaseRolePermission(BasePermission):
    required_role = None

    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return self.required_role == Role.USER
        return request.user.role == self.required_role


class RoleIsAdmin(BaseRolePermission):
    required_role = Role.ADMIN


class RoleIsManager(BaseRolePermission):
    required_role = Role.MANAGER

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.method != "DELETE"        


class RoleIsUser(BaseRolePermission):
    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return request.method in SAFE_METHODS
        return (
            request.user.role == Role.USER
            and request.method in SAFE_METHODS
        )


class ReviewPermission(BasePermission):
    def has_permission(self, request, view):
        if view.action in ["list", "retrieve", "create"]:
            return True
        if view.action == "destroy":
            return (
                request.user.is_authenticated
                and hasattr(request.user, "role")
                and request.user.role in [Role.ADMIN]
            )
        return False
