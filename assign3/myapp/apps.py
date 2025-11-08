from django.apps import AppConfig


class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        """Run startup tasks when Django starts."""
        # Import here to avoid AppRegistryNotReady error
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType
        from .models import Post, Comment
        
        # Auto-create roles if they don't exist
        try:
            self._create_default_groups()
        except Exception:
            # Skip during migrations or if database not ready
            pass

    def _create_default_groups(self):
        """Create Admin, Author, Reader groups with permissions."""
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType
        from .models import Post, Comment
        
        post_ct = ContentType.objects.get_for_model(Post)
        comment_ct = ContentType.objects.get_for_model(Comment)

        groups_config = {
            'Admin': [
                ('add_post', post_ct), ('change_post', post_ct),
                ('delete_post', post_ct), ('view_post', post_ct),
                ('add_comment', comment_ct), ('change_comment', comment_ct),
                ('delete_comment', comment_ct), ('view_comment', comment_ct),
            ],
            'Author': [
                ('add_post', post_ct), ('change_post', post_ct),
                ('delete_post', post_ct), ('view_post', post_ct),
                ('view_comment', comment_ct), ('change_comment', comment_ct),
                ('delete_comment', comment_ct),
            ],
            'Reader': [
                ('view_post', post_ct),
                ('add_comment', comment_ct), ('view_comment', comment_ct),
            ],
        }

        for group_name, perms in groups_config.items():
            group, created = Group.objects.get_or_create(name=group_name)
            if created or group.permissions.count() == 0:
                permissions = [
                    Permission.objects.get(codename=code, content_type=ct)
                    for code, ct in perms
                ]
                group.permissions.set(permissions)

