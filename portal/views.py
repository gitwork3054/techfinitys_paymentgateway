import io, base64, hashlib, hmac, json, uuid
from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import qrcode, qrcode.image.svg
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from .models import Payment, PaymentLog


def ip_of(r):
    forwarded = r.META.get("HTTP_X_FORWARDED_FOR", "")
    return forwarded.split(",")[0].strip() if forwarded else r.META.get("REMOTE_ADDR")


def log(r, client, event, detail="", payment=None):
    PaymentLog.objects.create(client=client, payment=payment, event=event, detail=detail[:255], ip=ip_of(r))


def client_of(r):
    c = getattr(r.user, "client", None)
    if not c:
        raise PermissionError("No client profile linked to this user")
    return c


def current_invoice(c):
    yr = c.due_date.year
    p, _ = Payment.objects.get_or_create(
        client=c,
        year=yr,
        defaults={"invoice_no": f"TFY-{yr}-{c.pk:03d}", "amount": c.yearly_amount},
    )
    return p


def brand_context(c, p=None):
    amount = p.amount if p else c.yearly_amount
    try:
        amount_int = int(amount)
    except Exception:
        amount_int = 0
    return {
        "company": settings.COMPANY,
        "brand": settings.CLIENT_BRAND,
        "package": settings.PACKAGE_DETAILS,
        "quick_amounts": settings.PACKAGE_DETAILS.get("quick_amounts", []),
        "selected_amount": amount_int,
    }


def cashfree_configured():
    return bool(settings.CASHFREE_CLIENT_ID and settings.CASHFREE_CLIENT_SECRET)


def cashfree_api(path, method="GET", payload=None):
    base = "https://sandbox.cashfree.com/pg" if settings.CASHFREE_ENV == "sandbox" else "https://api.cashfree.com/pg"
    body = json.dumps(payload).encode() if payload is not None else None
    req = Request(base + path, data=body, method=method, headers={
        "Accept": "application/json",
        "Content-Type": "application/json",
        "x-api-version": "2025-01-01",
        "x-client-id": settings.CASHFREE_CLIENT_ID,
        "x-client-secret": settings.CASHFREE_CLIENT_SECRET,
    })
    try:
        with urlopen(req, timeout=18) as res:
            return json.loads(res.read().decode())
    except HTTPError as e:
        try:
            detail = e.read().decode()
        except Exception:
            detail = str(e)
        raise RuntimeError(f"Cashfree API error ({e.code}): {detail[:300]}")
    except URLError as e:
        raise RuntimeError(f"Cashfree network error: {e.reason}")


def cashfree_create_order(request, client, payment, method):
    order_id = f"TFY-{payment.pk}-{uuid.uuid4().hex[:12].upper()}"
    phone = ''.join(ch for ch in (client.phone or '') if ch.isdigit())[-10:]
    if len(phone) != 10:
        phone = settings.CASHFREE_FALLBACK_PHONE
    payload = {
        "order_amount": float(payment.amount),
        "order_currency": "INR",
        "order_id": order_id,
        "customer_details": {
            "customer_id": f"tf_client_{client.pk}",
            "customer_phone": phone,
        },
        "order_note": f"Techfinitys annual licence - {payment.invoice_no}",
        "order_meta": {
            "return_url": request.build_absolute_uri(reverse("dashboard")) + "?payment_return={order_id}",
            "notify_url": request.build_absolute_uri(reverse("payment_webhook")),
            "payment_methods": "cc,dc" if method == "card" else "upi",
        },
    }
    if request.user.email:
        payload["customer_details"]["customer_email"] = request.user.email
    data = cashfree_api("/orders", "POST", payload)
    payment.provider = "Cashfree"
    payment.provider_order_id = order_id
    payment.app = "Card" if method == "card" else "UPI"
    payment.save(update_fields=["provider", "provider_order_id", "app"])
    return data


def cashfree_sync(payment, request=None):
    if payment.status == "paid" or not cashfree_configured() or payment.provider != "Cashfree" or not payment.provider_order_id:
        return payment
    try:
        rows = cashfree_api(f"/orders/{payment.provider_order_id}/payments")
    except RuntimeError:
        return payment
    if not isinstance(rows, list):
        return payment
    success = next((x for x in rows if x.get("payment_status") == "SUCCESS"), None)
    if success:
        method = success.get("payment_group") or success.get("payment_method", {}).get("card", {}).get("card_type") or payment.app or "Online"
        return complete_payment(payment, str(success.get("cf_payment_id") or success.get("payment_id") or payment.provider_order_id), str(method), request)
    if rows and all(x.get("payment_status") in {"FAILED", "USER_DROPPED", "CANCELLED"} for x in rows):
        payment.status = "failed"
        payment.save(update_fields=["status"])
    return payment

def complete_payment(payment, provider_payment_id, app="UPI", request=None):
    if payment.status == "paid":
        return payment
    payment.status = "paid"
    payment.provider_payment_id = provider_payment_id[:100]
    payment.app = app[:30]
    payment.paid_at = timezone.now()
    if not payment.slip_no:
        payment.slip_no = f"TF-RCP-{payment.paid_at:%Y%m%d}-{payment.pk:05d}"
    payment.save(update_fields=["status", "provider_payment_id", "app", "paid_at", "slip_no"])
    PaymentLog.objects.create(
        client=payment.client,
        payment=payment,
        event="PAYMENT_CONFIRMED",
        detail=f"Verified automatically by {payment.provider or 'payment provider'} · {payment.provider_payment_id}"[:255],
        ip=ip_of(request) if request else None,
    )
    return payment


@login_required
def dashboard(r):
    c = client_of(r)
    p = current_invoice(c)
    returned_order = r.GET.get("payment_return")
    if returned_order and p.provider_order_id == returned_order:
        p = cashfree_sync(p, r)
    ctx = {"c": c, "p": p, "recent": c.payments.filter(status="paid")[:3]}
    ctx.update(brand_context(c, p))
    return render(r, "portal/dashboard.html", ctx)

@login_required
def records(r):
    c = client_of(r)
    p = current_invoice(c)
    ctx = {"c": c, "p": p, "payments": c.payments.all(), "logs": c.logs.all()[:60]}
    ctx.update(brand_context(c, p))
    return render(r, "portal/records.html", ctx)

@login_required
def profile(r):
    c = client_of(r)
    ctx = {"c": c}
    ctx.update(brand_context(c, current_invoice(c)))
    return render(r, "portal/profile.html", ctx)

@login_required
@require_POST
def pay_start(r):
    c = client_of(r)
    p = current_invoice(c)
    if p.status == "paid":
        return JsonResponse({"error": "This invoice is already paid."}, status=400)

    amount_raw = (r.POST.get("amount") or "").replace(",", "").replace("₹", "").strip()
    if amount_raw:
        try:
            amount = Decimal(amount_raw)
        except InvalidOperation:
            return JsonResponse({"error": "Enter a valid payable amount."}, status=400)
        if amount <= 0:
            return JsonResponse({"error": "Amount must be greater than zero."}, status=400)
        p.amount = amount.quantize(Decimal("0.01"))
        p.save(update_fields=["amount"])

    p.provider = "Direct UPI"
    p.provider_order_id = f"TFY-{p.pk}-{uuid.uuid4().hex[:12].upper()}"
    p.app = "UPI"
    p.save(update_fields=["provider", "provider_order_id", "app"])

    q = urlencode({
        "pa": settings.UPI_ID,
        "pn": settings.UPI_NAME,
        "am": f"{p.amount:.2f}",
        "cu": "INR",
        "tn": f"Techfinitys {p.invoice_no}",
        "tr": p.provider_order_id,
    })
    upi_url = "upi://pay?" + q
    img = qrcode.make(upi_url, image_factory=qrcode.image.svg.SvgPathImage, box_size=10)
    buf = io.BytesIO()
    img.save(buf)
    log(r, c, "PAYMENT_INITIATED", f"{p.invoice_no} · direct UPI · amount {p.amount}", p)

    return JsonResponse({
        "id": p.pk,
        "order_id": p.provider_order_id,
        "gateway": "direct_upi",
        "qr": "data:image/svg+xml;base64," + base64.b64encode(buf.getvalue()).decode(),
        "upi_id": settings.UPI_ID,
        "upi_url": upi_url,
        "amount": f"{p.amount:.2f}",
    })

@login_required
@require_GET
def payment_status(r, pk):
    c = client_of(r)
    p = get_object_or_404(Payment, pk=pk, client=c)
    p = cashfree_sync(p, r)
    payload = {"status": p.status, "invoice": p.invoice_no}
    if p.status == "paid":
        payload.update({
            "paid_at": p.paid_at.isoformat() if p.paid_at else None,
            "payment_id": p.provider_payment_id,
            "slip_url": reverse("slip", args=[p.pk]),
        })
    return JsonResponse(payload)


@csrf_exempt
@require_POST
def payment_webhook(r):
    raw = r.body

    cf_signature = r.headers.get("X-Webhook-Signature", "").strip()
    cf_timestamp = r.headers.get("X-Webhook-Timestamp", "").strip()
    if cf_signature and cf_timestamp and cashfree_configured():
        signed = cf_timestamp.encode() + raw
        expected = base64.b64encode(hmac.new(settings.CASHFREE_CLIENT_SECRET.encode(), signed, hashlib.sha256).digest()).decode()
        if not hmac.compare_digest(cf_signature, expected):
            return JsonResponse({"error": "Invalid Cashfree webhook signature"}, status=401)
        try:
            data = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return HttpResponseBadRequest("Invalid JSON")
        order_id = str((data.get("data") or {}).get("order", {}).get("order_id") or data.get("order_id") or "")
        if not order_id:
            return JsonResponse({"error": "Missing order_id"}, status=400)
        try:
            p = Payment.objects.get(provider_order_id=order_id)
        except Payment.DoesNotExist:
            return JsonResponse({"error": "Unknown order"}, status=404)
        p = cashfree_sync(p, r)
        log(r, p.client, "PAYMENT_WEBHOOK", f"Cashfree callback · {data.get('type','event')} · status {p.status}", p)
        return JsonResponse({"ok": True, "status": p.status})

    secret = settings.PAYMENT_WEBHOOK_SECRET.encode()
    received = r.headers.get("X-Techfinitys-Signature", "").strip()
    expected = hmac.new(secret, raw, hashlib.sha256).hexdigest()
    if not secret or not received or not hmac.compare_digest(received, expected):
        return JsonResponse({"error": "Invalid webhook signature"}, status=401)
    try:
        data = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return HttpResponseBadRequest("Invalid JSON")

    event = data.get("event")
    order_id = str(data.get("order_id", ""))
    provider_payment_id = str(data.get("payment_id", ""))
    if not order_id:
        return JsonResponse({"error": "Missing order_id"}, status=400)

    with transaction.atomic():
        try:
            p = Payment.objects.select_for_update().get(provider_order_id=order_id)
        except Payment.DoesNotExist:
            return JsonResponse({"error": "Unknown order"}, status=404)
        if event in {"payment.success", "payment.captured", "payment.paid"}:
            if not provider_payment_id:
                return JsonResponse({"error": "Missing payment_id"}, status=400)
            complete_payment(p, provider_payment_id, str(data.get("app", "Online")), r)
        elif event in {"payment.failed", "payment.cancelled"} and p.status != "paid":
            p.status = "failed"
            p.save(update_fields=["status"])
            log(r, p.client, "PAYMENT_FAILED", f"Provider event: {event}", p)
        else:
            log(r, p.client, "PAYMENT_WEBHOOK", f"Ignored provider event: {event}", p)
    return JsonResponse({"ok": True})


@login_required
def slip(r, pk):
    c = client_of(r)
    p = get_object_or_404(Payment, pk=pk, client=c, status="paid")
    log(r, c, "SLIP_VIEWED", p.slip_no, p)
    return render(r, "portal/slip.html", {"c": c, "p": p, "company": settings.COMPANY})
