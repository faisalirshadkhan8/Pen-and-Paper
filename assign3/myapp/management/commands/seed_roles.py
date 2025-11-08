from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from myapp.models import Post, Comment


class Command(BaseCommand):
    help = 'Create default user groups (Admin, Author, Reader) with appropriate permissions'

    def handle(self, *args, **kwargs):
        # Get content types
        post_ct = ContentType.objects.get_for_model(Post)
        comment_ct = ContentType.objects.get_for_model(Comment)

        # Define groups and their permissions
        groups_permissions = {
            'Admin': {
                'description': 'Full access to all posts, comments, and admin features',
                'permissions': [
                    # Post permissions (all)
                    Permission.objects.get(codename='add_post', content_type=post_ct),
                    Permission.objects.get(codename='change_post', content_type=post_ct),
                    Permission.objects.get(codename='delete_post', content_type=post_ct),
                    Permission.objects.get(codename='view_post', content_type=post_ct),
                    # Comment permissions (all)
                    Permission.objects.get(codename='add_comment', content_type=comment_ct),
                    Permission.objects.get(codename='change_comment', content_type=comment_ct),
                    Permission.objects.get(codename='delete_comment', content_type=comment_ct),
                    Permission.objects.get(codename='view_comment', content_type=comment_ct),
                ]
            },
            'Author': {
                'description': 'Can create, edit, and delete own posts',
                'permissions': [
                    # Post permissions (CRUD on own posts)
                    Permission.objects.get(codename='add_post', content_type=post_ct),
                    Permission.objects.get(codename='change_post', content_type=post_ct),
                    Permission.objects.get(codename='delete_post', content_type=post_ct),
                    Permission.objects.get(codename='view_post', content_type=post_ct),
                    # Comment permissions (view and moderate)
                    Permission.objects.get(codename='view_comment', content_type=comment_ct),
                    Permission.objects.get(codename='change_comment', content_type=comment_ct),
                    Permission.objects.get(codename='delete_comment', content_type=comment_ct),
                ]
            },
            'Reader': {
                'description': 'Can view posts and add comments',
                'permissions': [
                    # Post permissions (view only)
                    Permission.objects.get(codename='view_post', content_type=post_ct),
                    # Comment permissions (add and view own)
                    Permission.objects.get(codename='add_comment', content_type=comment_ct),
                    Permission.objects.get(codename='view_comment', content_type=comment_ct),
                ]
            },
        }

        # Create groups
        created_count = 0
        updated_count = 0

        for group_name, group_data in groups_permissions.items():
            group, created = Group.objects.get_or_create(name=group_name)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created group: {group_name}'))
                created_count += 1
            else:
                self.stdout.write(self.style.WARNING(f'→ Group already exists: {group_name}'))
                updated_count += 1

            # Clear existing permissions and set new ones
            group.permissions.clear()
            group.permissions.set(group_data['permissions'])
            
            self.stdout.write(f'  {group_data["description"]}')
            self.stdout.write(f'  Permissions: {group.permissions.count()}')
            self.stdout.write('')

        # Summary
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS(f'Groups created: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'Groups updated: {updated_count}'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('')
        self.stdout.write('Next steps:')
        self.stdout.write('1. Go to /admin/auth/user/')
        self.stdout.write('2. Edit a user')
        self.stdout.write('3. Add them to "Author" or "Reader" group')
        self.stdout.write('4. Superusers automatically have all permissions')
