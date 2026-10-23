import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Create or update the production admin from environment variables."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin").strip() or "admin"
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")

        if not password:
            raise CommandError(
                "DJANGO_SUPERUSER_PASSWORD is missing. Add it in Render > Environment and deploy again."
            )

        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()
        User = get_user_model()
        user, created = User.objects.get_or_create(username=username)

        user.email = email or user.email
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()

        user.refresh_from_db()
        if not user.check_password(password):
            raise CommandError("Admin password verification failed after saving.")

        self.stdout.write(
            self.style.SUCCESS(
                f"ADMIN_LOGIN_READY username={username} created={created} staff={user.is_staff} superuser={user.is_superuser}"
            )
        )
