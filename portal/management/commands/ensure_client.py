import os
from datetime import date
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from portal.models import Client

class Command(BaseCommand):
    help = "Create or update the production client login and Client profile from environment variables."

    def handle(self, *args, **options):
        username = os.environ.get("CLIENT_USERNAME", "ashapurarakhi").strip() or "client"
        password = os.environ.get("CLIENT_PASSWORD", "")
        if not password:
            raise CommandError("CLIENT_PASSWORD is missing. Add it in Render > Environment and deploy again.")

        User = get_user_model()
        user, created_user = User.objects.get_or_create(username=username)
        user.set_password(password)
        user.is_active = True
        user.is_staff = False
        user.is_superuser = False
        email = os.environ.get("CLIENT_EMAIL", "").strip()
        if email:
            user.email = email
        user.save()
        user.refresh_from_db()
        if not user.check_password(password):
            raise CommandError("Client password verification failed after saving.")

        due_raw = os.environ.get("CLIENT_DUE_DATE", "2026-12-28")
        try:
            due_date = date.fromisoformat(due_raw)
        except ValueError:
            raise CommandError("CLIENT_DUE_DATE must use YYYY-MM-DD format.")

        try:
            yearly_amount = Decimal(os.environ.get("CLIENT_YEARLY_AMOUNT", "300000"))
        except Exception:
            raise CommandError("CLIENT_YEARLY_AMOUNT must be a valid number.")

        defaults = {
            "company": os.environ.get("CLIENT_COMPANY", "Ashapura Rakhi"),
            "contact": os.environ.get("CLIENT_CONTACT", "Ashapura Rakhi"),
            "phone": os.environ.get("CLIENT_PHONE", "8401947462"),
            "gstin": os.environ.get("CLIENT_GSTIN", ""),
            "address": os.environ.get("CLIENT_ADDRESS", "Opposite Old Laxmipura Police Station, Laxmipura Road, Vadodara, Gujarat"),
            "project": "Billing Suite",
            "plan": os.environ.get("CLIENT_PLAN", "Premium Brand Growth Plan"),
            "yearly_amount": yearly_amount,
            "due_date": due_date,
        }
        client, created_client = Client.objects.get_or_create(user=user, defaults=defaults)
        if not created_client:
            for key, value in defaults.items():
                setattr(client, key, value)
            client.save()

        self.stdout.write(self.style.SUCCESS(
            f"CLIENT_LOGIN_READY username={username} user_created={created_user} profile_created={created_client}"
        ))
