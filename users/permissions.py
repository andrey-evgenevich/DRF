from rest_framework import permissions


class IsModer(permissions.BasePermission):
    """Модератор"""

    def has_permission(self, request, view):
        return request.user.groups.filter(name="Модератор").exists()


class IsOwner(permissions.BasePermission):
    """Владелец"""

    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True
        return False


class IsUser(permissions.BasePermission):
    """Пользователь"""

    def has_object_permission(self, request, view, obj):
        if obj == request.user:
            return True
        return False
