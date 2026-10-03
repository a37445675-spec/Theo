from rest_framework import permissions


class IsShopManagerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        return bool(
            user and user.is_authenticated
            and (user.is_superuser or user.groups.filter(name__in=["shop_manager", "administrator"]).exists())
        )


class IsVendorOwnerOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser or user.groups.filter(name__in=["shop_manager", "administrator"]).exists():
            return True
        owner_id = getattr(obj, "vendor_id", None) or getattr(obj, "customer_id", None)
        return owner_id == user.id


class IsOwner(permissions.BasePermission):
    owner_field = "customer"

    def has_object_permission(self, request, view, obj):
        return getattr(obj, self.owner_field, None) == request.user
