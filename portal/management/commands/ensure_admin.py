import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Create or update the production admin from environment variables."

    def handle(self, *args, **options):
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")
        if not password:
            self.stdout.write("DJANGO_SUPERUSER_PASSWORD not set; skipping admin bootstrap.")
            return
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")
        User = get_user_model()
        user, created = User.objects.get_or_create(username=username, defaults={"email": email})
        user.email = email or user.email
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(f"Admin {'created' if created else 'updated'}: {username}"))
