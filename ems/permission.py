from rest_framework.permissions import BasePermission


class IsArtistUser(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        print(user.is_artist)
        if user.is_artist:
            return True
        else:
            return False
