import os
from datetime import date
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from portal.models import Client

class Command(BaseCommand):
    help = "Create or update the production client user and Client profile from environment variables."

    def handle(self, *args, **options):
        username = os.environ.get("CLIENT_USERNAME", "").strip()
        password = os.environ.get("CLIENT_PASSWORD", "")
        if not username or not password:
            self.stdout.write("CLIENT_USERNAME/CLIENT_PASSWORD not set; skipping client bootstrap.")
            return

        User = get_user_model()
        user, _ = User.objects.get_or_create(username=username)
        user.set_password(password)
        user.is_active = True
        user.is_staff = False
        user.is_superuser = False
        email = os.environ.get("CLIENT_EMAIL", "").strip()
        if email:
            user.email = email
        user.save()

        due_raw = os.environ.get("CLIENT_DUE_DATE", "2026-12-31")
        try:
            due_date = date.fromisoformat(due_raw)
        except ValueError:
            due_date = date(2026, 12, 31)

        defaults = {
            "company": os.environ.get("CLIENT_COMPANY", "Client Company"),
            "contact": os.environ.get("CLIENT_CONTACT", username),
            "phone": os.environ.get("CLIENT_PHONE", ""),
            "gstin": os.environ.get("CLIENT_GSTIN", ""),
            "address": os.environ.get("CLIENT_ADDRESS", ""),
            "project": os.environ.get("CLIENT_PROJECT", "Software Project"),
            "plan": os.environ.get("CLIENT_PLAN", "Enterprise Annual"),
            "yearly_amount": Decimal(os.environ.get("CLIENT_YEARLY_AMOUNT", "400000")),
            "due_date": due_date,
        }
        client, created = Client.objects.get_or_create(user=user, defaults=defaults)
        if not created:
            for k, v in defaults.items():
                setattr(client, k, v)
            client.save()

        self.stdout.write(self.style.SUCCESS(f"Client {'created' if created else 'updated'}: {username}"))
