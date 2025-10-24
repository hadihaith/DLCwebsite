"""
Management command to create a superuser non-interactively.
Usage: python manage.py create_admin
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates an admin superuser non-interactively if it does not exist'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='admin', help='Admin username')
        parser.add_argument('--email', default='admin@dlccba.live', help='Admin email')
        parser.add_argument('--password', default='admin123', help='Admin password')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name='Hadi',
                last_name='Haidar',  # Required by your custom User model
            )
            self.stdout.write(self.style.SUCCESS(f'✅ Superuser "{username}" created successfully!'))
            self.stdout.write(self.style.WARNING(f'   Email: {email}'))
            self.stdout.write(self.style.WARNING(f'   Password: {password}'))
            self.stdout.write(self.style.WARNING(f'   ⚠️  CHANGE THIS PASSWORD IMMEDIATELY!'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠️  Superuser "{username}" already exists.'))
