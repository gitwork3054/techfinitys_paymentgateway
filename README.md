# Techfinitys Payment Gateway

Premium Django client portal with annual billing, payment records, receipts, light/dark UI, and Cashfree-ready UPI + debit/credit-card checkout.

## Local run

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed
python manage.py runserver
```

Demo seed command creates local demo users only. Do not use the demo passwords for production.

## Render deployment

This repository includes `render.yaml` and `build.sh` for Render Blueprint deployment. Render provisions PostgreSQL, runs `collectstatic` + migrations, and starts Gunicorn automatically.

Required Render secrets:

- `CASHFREE_CLIENT_ID`
- `CASHFREE_CLIENT_SECRET`
- `CASHFREE_FALLBACK_PHONE`

Render generates `DJANGO_SECRET_KEY` automatically. Keep `CASHFREE_ENV=sandbox` until Cashfree production onboarding is approved.

After the first deployment, create production accounts from the Render Shell instead of running the demo seed command:

```bash
python manage.py createsuperuser
```

Cashfree webhook endpoint:

```text
https://YOUR-RENDER-HOST/webhooks/payment/
```

Never commit payment gateway secrets to GitHub.
