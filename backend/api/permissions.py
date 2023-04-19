from rest_framework import permissions


class IsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )


class AuthorStaffOrReadOnly(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_active
            and (request.user == obj.author or request.user.is_staff)
        )


class AdminOrReadOnly(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_active
            and request.user.is_staff
        )


class OwnerUserOrReadOnly(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_active
            and request.user == obj.author
            or request.user.is_staff
        )
