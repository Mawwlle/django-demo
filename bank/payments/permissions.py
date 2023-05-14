from rest_framework import permissions


class IsOwner(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj) -> bool:
        return obj.owner == request.user


class IsAccountTransaction(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj) -> bool:
        return obj.account.owner == request.user


class IsReadOnly(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        return request.method in permissions.SAFE_METHODS
