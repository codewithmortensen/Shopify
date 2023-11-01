from rest_framework.permissions import DjangoModelPermissions


class ShopifyModelPermission(DjangoModelPermissions):
    def __init__(self) -> None:
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
