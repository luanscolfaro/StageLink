from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsContractor(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.account_type == "contractor")


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.owner_id == request.user.id
