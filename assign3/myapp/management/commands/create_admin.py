from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os


class Command(BaseCommand):
    help = 'Create a superuser from environment variables'

    def handle(self, *args, **kwargs):
        username = os.environ.get('ADMIN_USERNAME', 'admin')
        email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
        password = os.environ.get('ADMIN_PASSWORD')
        
        if not password:
            self.stdout.write(self.style.ERROR('ADMIN_PASSWORD environment variable not set!'))
            return
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'User {username} already exists'))
            return
        
        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f'Superuser {username} created successfully!'))
