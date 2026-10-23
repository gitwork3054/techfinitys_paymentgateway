from django.urls import path
from django.contrib.auth import views as av
from . import views as v

urlpatterns = [
    path("", v.dashboard, name="dashboard"),
    path("login/", av.LoginView.as_view(template_name="portal/login.html"), name="login"),
    path("logout/", av.LogoutView.as_view(), name="logout"),
    path("profile/", v.profile, name="profile"),
    path("records/", v.records, name="records"),
    path("pay/start/", v.pay_start, name="pay_start"),
    path("pay/<int:pk>/status/", v.payment_status, name="payment_status"),
    path("webhooks/payment/", v.payment_webhook, name="payment_webhook"),
    path("slip/<int:pk>/", v.slip, name="slip"),
]
