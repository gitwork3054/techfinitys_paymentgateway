import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.CharField(max_length=120)
    contact = models.CharField(max_length=120)
    phone = models.CharField(max_length=20, blank=True)
    gstin = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    project = models.CharField(max_length=160)
    plan = models.CharField(max_length=60, default="Enterprise Annual")
    yearly_amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()
    since = models.DateField(default=timezone.now)
    def __str__(self): return self.company

class Payment(models.Model):
    STATUS = [("pending","Pending"),("paid","Paid"),("failed","Failed")]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="payments")
    invoice_no = models.CharField(max_length=30, unique=True)
    year = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS, default="pending")
    app = models.CharField(max_length=30, blank=True)
    utr = models.CharField(max_length=30, blank=True)
    provider = models.CharField(max_length=30, blank=True)
    provider_order_id = models.CharField(max_length=80, blank=True, db_index=True)
    provider_payment_id = models.CharField(max_length=100, blank=True, db_index=True)
    slip_no = models.CharField(max_length=30, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    class Meta: ordering = ["-created"]
    def __str__(self): return self.invoice_no

class PaymentLog(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="logs")
    payment = models.ForeignKey(Payment, null=True, on_delete=models.SET_NULL)
    event = models.CharField(max_length=40)
    detail = models.CharField(max_length=255, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["-at"]
