from rest_framework.permissions import DjangoModelPermissions, BasePermission


class ShopifyModelPermission(DjangoModelPermissions):
    def __init__(self) -> None:
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']


class IsReviewOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not hasattr(user, 'customer'):
            return False

        return bool(request.user.customer == obj.customer)
