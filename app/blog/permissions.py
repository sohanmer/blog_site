"""Custom permission class to exclude list API from authentication."""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class AuthenticatedOrListOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method == 'GET' and view.action == 'list'
            or request.user and request.user.is_authenticated
        )
    

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user
