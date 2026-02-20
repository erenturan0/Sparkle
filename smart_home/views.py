import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import SmartDevice
from .services import tasmota


# ═══════════════════════════════════════════════════════════
#  AUTH VIEWS
# ═══════════════════════════════════════════════════════════

def login_view(request):
    """Giriş sayfası."""
    if request.user.is_authenticated:
        return redirect("smart_home:dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get("next", "/")
            return redirect(next_url)
        else:
            return render(request, "smart_home/login.html", {
                "error": "Kullanıcı adı veya şifre hatalı.",
                "username": username,
            })

    return render(request, "smart_home/login.html")


def register_view(request):
    """Kayıt sayfası."""
    if request.user.is_authenticated:
        return redirect("smart_home:dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        errors = []

        if not username:
            errors.append("Kullanıcı adı boş bırakılamaz.")
        elif len(username) < 3:
            errors.append("Kullanıcı adı en az 3 karakter olmalı.")
        elif User.objects.filter(username=username).exists():
            errors.append("Bu kullanıcı adı zaten kullanılıyor.")

        if not email:
            errors.append("E-posta adresi boş bırakılamaz.")
        elif User.objects.filter(email=email).exists():
            errors.append("Bu e-posta adresi zaten kullanılıyor.")

        if len(password1) < 8:
            errors.append("Şifre en az 8 karakter olmalı.")
        elif password1 != password2:
            errors.append("Şifreler eşleşmiyor.")

        if errors:
            return render(request, "smart_home/register.html", {
                "errors": errors,
                "form_data": {"username": username, "email": email},
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
        )
        login(request, user)
        return redirect("smart_home:dashboard")

    return render(request, "smart_home/register.html")


def logout_view(request):
    """Çıkış yap ve giriş sayfasına yönlendir."""
    logout(request)
    return redirect("smart_home:login")


# ═══════════════════════════════════════════════════════════
#  DASHBOARD
# ═══════════════════════════════════════════════════════════

@login_required
def dashboard(request):
    """Ana sayfa — Akıllı Ev Dashboard."""
    devices = SmartDevice.objects.filter(is_active=True)

    total = devices.count()
    rooms = devices.values("room").distinct().count()

    context = {
        "devices": devices,
        "stats": {
            "total": total,
            "rooms": rooms,
        },
        "active_nav": "dashboard",
    }
    return render(request, "smart_home/dashboard.html", context)


# ═══════════════════════════════════════════════════════════
#  DEVICE CRUD
# ═══════════════════════════════════════════════════════════

@login_required
def devices_list(request):
    """Cihaz listesi sayfası."""
    devices = SmartDevice.objects.all()
    return render(request, "smart_home/devices.html", {
        "devices": devices,
        "active_nav": "devices",
    })


@login_required
def device_add(request):
    """Yeni cihaz ekleme."""
    if request.method == "POST":
        return _save_device(request)

    return render(request, "smart_home/device_form.html", {
        "editing": False,
        "rooms": SmartDevice.Room.choices,
        "device_types": SmartDevice.DeviceType.choices,
        "form_data": {},
        "active_nav": "devices",
    })


@login_required
def device_edit(request, device_id):
    """Cihaz düzenleme."""
    device = get_object_or_404(SmartDevice, pk=device_id)

    if request.method == "POST":
        return _save_device(request, device)

    return render(request, "smart_home/device_form.html", {
        "editing": True,
        "rooms": SmartDevice.Room.choices,
        "device_types": SmartDevice.DeviceType.choices,
        "form_data": {
            "name": device.name,
            "ip_address": device.ip_address,
            "room": device.room,
            "device_type": device.device_type,
            "is_active": device.is_active,
        },
        "active_nav": "devices",
    })


def _save_device(request, device=None):
    """Cihaz kaydetme yardımcı fonksiyonu (add/edit ortak)."""
    name = request.POST.get("name", "").strip()
    ip_address = request.POST.get("ip_address", "").strip()
    room = request.POST.get("room", "")
    device_type = request.POST.get("device_type", "")
    is_active = request.POST.get("is_active") == "1"

    errors = []

    if not name:
        errors.append("Cihaz adı boş bırakılamaz.")
    if not ip_address:
        errors.append("IP adresi boş bırakılamaz.")
    else:
        # Aynı IP'ye sahip başka cihaz var mı?
        ip_query = SmartDevice.objects.filter(ip_address=ip_address)
        if device:
            ip_query = ip_query.exclude(pk=device.pk)
        if ip_query.exists():
            errors.append("Bu IP adresi başka bir cihaz tarafından kullanılıyor.")

    form_data = {
        "name": name,
        "ip_address": ip_address,
        "room": room,
        "device_type": device_type,
        "is_active": is_active,
    }

    if errors:
        return render(request, "smart_home/device_form.html", {
            "editing": device is not None,
            "rooms": SmartDevice.Room.choices,
            "device_types": SmartDevice.DeviceType.choices,
            "form_data": form_data,
            "errors": errors,
            "active_nav": "devices",
        })

    if device is None:
        device = SmartDevice()

    device.name = name
    device.ip_address = ip_address
    device.room = room
    device.device_type = device_type
    device.is_active = is_active
    device.save()

    messages.success(request, f"\"{device.name}\" {'güncellendi' if device.pk else 'eklendi'}.")
    return redirect("smart_home:devices")


@login_required
@require_POST
def device_delete(request, device_id):
    """Cihaz silme."""
    device = get_object_or_404(SmartDevice, pk=device_id)
    device_name = device.name
    device.delete()
    messages.success(request, f"\"{device_name}\" silindi.")
    return redirect("smart_home:devices")


# ═══════════════════════════════════════════════════════════
#  SETTINGS
# ═══════════════════════════════════════════════════════════

@login_required
def settings_view(request):
    """Ayarlar sayfası."""
    return render(request, "smart_home/settings.html", {
        "active_nav": "settings",
    })


@login_required
@require_POST
def settings_profile(request):
    """Profil bilgilerini güncelle."""
    username = request.POST.get("username", "").strip()
    email = request.POST.get("email", "").strip()
    user = request.user

    errors = []

    if not username:
        errors.append("Kullanıcı adı boş bırakılamaz.")
    elif len(username) < 3:
        errors.append("Kullanıcı adı en az 3 karakter olmalı.")
    elif User.objects.filter(username=username).exclude(pk=user.pk).exists():
        errors.append("Bu kullanıcı adı zaten kullanılıyor.")

    if not email:
        errors.append("E-posta adresi boş bırakılamaz.")
    elif User.objects.filter(email=email).exclude(pk=user.pk).exists():
        errors.append("Bu e-posta adresi zaten kullanılıyor.")

    if errors:
        return render(request, "smart_home/settings.html", {
            "errors": errors,
            "active_nav": "settings",
        })

    user.username = username
    user.email = email
    user.save()
    messages.success(request, "Profil bilgilerin güncellendi.")
    return redirect("smart_home:settings")


@login_required
@require_POST
def settings_password(request):
    """Şifre değiştir."""
    current_password = request.POST.get("current_password", "")
    new_password1 = request.POST.get("new_password1", "")
    new_password2 = request.POST.get("new_password2", "")
    user = request.user

    errors = []

    if not user.check_password(current_password):
        errors.append("Mevcut şifre hatalı.")

    if len(new_password1) < 8:
        errors.append("Yeni şifre en az 8 karakter olmalı.")
    elif new_password1 != new_password2:
        errors.append("Yeni şifreler eşleşmiyor.")

    if errors:
        return render(request, "smart_home/settings.html", {
            "errors": errors,
            "active_nav": "settings",
        })

    user.set_password(new_password1)
    user.save()
    update_session_auth_hash(request, user)  # Oturumu koru
    messages.success(request, "Şifren başarıyla güncellendi.")
    return redirect("smart_home:settings")


# ═══════════════════════════════════════════════════════════
#  API
# ═══════════════════════════════════════════════════════════

@login_required
@require_POST
def api_toggle(request, device_id):
    """Tasmota cihaz toggle API endpoint'i."""
    device = get_object_or_404(SmartDevice, pk=device_id, is_active=True)

    result = tasmota.toggle(device.ip_address)

    if result is None:
        return JsonResponse(
            {"ok": False, "error": f"{device.name} cihazına ulaşılamıyor."},
            status=503,
        )

    power = result.get("POWER", "UNKNOWN")

    device.last_seen = timezone.now()
    device.save(update_fields=["last_seen"])

    return JsonResponse({"ok": True, "power": power})
