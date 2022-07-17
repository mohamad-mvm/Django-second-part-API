from rest_framework.permissions import BasePermission , DjangoModelPermissions 

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return (request.user and request.user.is_staff)

class FullDjangoModelPermissions(DjangoModelPermissions):

    def __init__(self) -> None:
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']

