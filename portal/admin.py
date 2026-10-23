from django.contrib import admin
from .models import Client, Payment, PaymentLog
admin.site.register(Client)
@admin.register(Payment)
class PA(admin.ModelAdmin): list_display=("invoice_no","client","amount","status","provider","provider_payment_id","paid_at")
@admin.register(PaymentLog)
class LA(admin.ModelAdmin): list_display=("at","client","event","detail","ip")
