from rest_framework import permissions
from django.contrib.auth.models import User

#custom permission to give full access, read write to the super_user and give read_only access to other users in the view level and object level
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_superuser
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_superuser or request.user==obj.owner
    
