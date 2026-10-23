# Techfinitys Payment Gateway

Premium Django client portal with annual billing, payment records, automatic verified receipts, dark/light UI, and Cashfree-ready UPI + debit/credit-card checkout.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/gitwork3054/techfinitys_paymentgateway)

## Render deployment

The root `render.yaml` provisions the Django web service and PostgreSQL database. During the first Blueprint deploy, Render asks for `DJANGO_SUPERUSER_PASSWORD`; choose a strong password. The username is `admin`.

After deployment:

1. Open `https://YOUR-SERVICE.onrender.com/admin/` and sign in as `admin`.
2. Create the client login under **Users**.
3. Create its matching **Client** profile with annual amount, project and due date.
4. When Cashfree gives you API credentials, add `CASHFREE_CLIENT_ID` and `CASHFREE_CLIENT_SECRET` in Render → service → Environment.
5. Keep `CASHFREE_ENV=sandbox` for testing; change it to `production` only after Cashfree activates live payments.
6. Configure the Cashfree webhook URL as `https://YOUR-SERVICE.onrender.com/webhooks/payment/`.

Never commit gateway secrets or customer passwords to GitHub.

## Local run

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
