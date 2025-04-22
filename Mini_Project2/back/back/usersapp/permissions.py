from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the request user is the owner of the object
        is_owner = obj == request.user
        # Allow admin users and staff to access
        is_admin = request.user.is_staff or request.user.role == 'admin'
        # Return True if one of the conditions is met
        return is_owner or is_admin


class IsUserOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow users who created a resource or admins
    to access it.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the request user is the owner of the object
        is_owner = hasattr(obj, 'user') and obj.user == request.user
        # Allow admin users and staff to access
        is_admin = (request.user.is_staff or 
                   request.user.role == 'admin')
        # Return True if one of the conditions is met
        return is_owner or is_admin


class IsRecruiterOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow recruiters or admins to access certain views.
    """

    def has_permission(self, request, view):
        # Allow only recruiters and admins
        return (
            request.user.is_authenticated and 
            (request.user.role in ['recruiter', 'admin'] or 
             request.user.is_staff)
        )
    
    def has_object_permission(self, request, view, obj):
        # Check if the request user is the recruiter who created the object
        is_recruiter = (hasattr(obj, 'recruiter') and 
                        obj.recruiter == request.user)
        # Allow admin users and staff to access
        is_admin = request.user.is_staff or request.user.role == 'admin'
        # Return True if one of the conditions is met
        return is_recruiter or is_admin
