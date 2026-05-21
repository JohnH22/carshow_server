from rest_framework import permissions

# Custom permission to only allow owners of an object to edit or delete it (POST, PUT, DELETE)
# Allows anyone to view data (GET, HEAD, OPTIONS)
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # STEP 1: Check if the user is just looking (Read-only)
        # If the request method is GET, HEAD, OPTIONS its safe, allow it
        if request.method in permissions.SAFE_METHODS:
            return True

        # STEP 2: If the user wants to EDIT or DELETE , verify ownership

        # CASE A: If the object is a Vehicle (uses the field "owner")
        if hasattr(obj, 'owner'):
            # Returns True only if the logged-in user is the actual owner
            return obj.owner == request.user
        # CASE B: If the object is a Review (uses the field "user")
        # Returns True only if the logged-in user is the one who wrote the review
        return obj.user == request.user