from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_default_groups(sender, **kwargs):
    from django.contrib.auth.models import Group, Permission

    role_permissions = {
        'Standard User': ['add_album', 'view_album', 'add_photo', 'view_photo'],
        'Album Administrator': ['add_album', 'view_album', 'change_album', 'delete_album', 'add_photo', 'view_photo', 'change_photo', 'delete_photo', 'moderate_content'],
    }

    for group_name, codenames in role_permissions.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        permissions = Permission.objects.filter(codename__in=codenames)
        group.permissions.set(permissions)


class AlbumsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'albums'

    def ready(self):
        post_migrate.connect(create_default_groups, sender=self)
