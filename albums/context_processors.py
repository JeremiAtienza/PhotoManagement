def is_album_admin(request):
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return {'is_album_admin': False}

    return {
        'is_album_admin': user.is_superuser or user.groups.filter(name='Album Administrator').exists(),
    }
