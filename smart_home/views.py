import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import SmartDevice, DeviceShareRequest
from .services import tasmota


def login_view(request):
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
    logout(request)
    return redirect("smart_home:login")


@login_required
def dashboard(request):
    devices = SmartDevice.objects.filter(owner=request.user, is_active=True)

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


@login_required
def devices_list(request):
    devices = SmartDevice.objects.filter(owner=request.user)
    return render(request, "smart_home/devices.html", {
        "devices": devices,
        "active_nav": "devices",
    })


@login_required
def device_add(request):
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
    device = get_object_or_404(SmartDevice, pk=device_id, owner=request.user)

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
        own_query = SmartDevice.objects.filter(ip_address=ip_address, owner=request.user)
        if device:
            own_query = own_query.exclude(pk=device.pk)
        if own_query.exists():
            errors.append("Bu IP adresini zaten kullanıyorsun.")
        elif not errors:
            other_device = SmartDevice.objects.filter(ip_address=ip_address).exclude(owner=request.user).first()
            if other_device and device is None:
                existing = DeviceShareRequest.objects.filter(
                    requester=request.user,
                    ip_address=ip_address,
                    status=DeviceShareRequest.Status.PENDING,
                ).exists()
                if existing:
                    messages.info(request, "Bu IP için zaten bekleyen bir onay isteğiniz var.")
                    return redirect("smart_home:devices")
                DeviceShareRequest.objects.create(
                    requester=request.user,
                    owner=other_device.owner,
                    ip_address=ip_address,
                    device_name=name,
                    room=room,
                    device_type=device_type,
                )
                messages.success(request, f"\"{name}\" için cihaz sahibine onay isteği gönderildi.")
                return redirect("smart_home:devices")

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
        device = SmartDevice(owner=request.user)

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
    device = get_object_or_404(SmartDevice, pk=device_id, owner=request.user)
    device_name = device.name
    device.delete()
    messages.success(request, f"\"{device_name}\" silindi.")
    return redirect("smart_home:devices")


@login_required
def settings_view(request):
    return render(request, "smart_home/settings.html", {
        "active_nav": "settings",
    })


@login_required
@require_POST
def settings_profile(request):
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
    update_session_auth_hash(request, user)
    messages.success(request, "Şifren başarıyla güncellendi.")
    return redirect("smart_home:settings")


@login_required
@require_POST
def api_toggle(request, device_id):
    device = get_object_or_404(SmartDevice, pk=device_id, owner=request.user, is_active=True)

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


@login_required
def share_requests(request):
    pending = DeviceShareRequest.objects.filter(
        owner=request.user,
        status=DeviceShareRequest.Status.PENDING,
    )
    resolved = DeviceShareRequest.objects.filter(
        owner=request.user,
    ).exclude(status=DeviceShareRequest.Status.PENDING)[:20]

    sent = DeviceShareRequest.objects.filter(
        requester=request.user,
    ).order_by('-created_at')[:20]

    return render(request, "smart_home/share_requests.html", {
        "pending_requests": pending,
        "resolved_requests": resolved,
        "sent_requests": sent,
        "active_nav": "requests",
    })


@login_required
@require_POST
def share_request_approve(request, request_id):
    share_req = get_object_or_404(
        DeviceShareRequest,
        pk=request_id,
        owner=request.user,
        status=DeviceShareRequest.Status.PENDING,
    )

    SmartDevice.objects.create(
        owner=share_req.requester,
        name=share_req.device_name,
        ip_address=share_req.ip_address,
        room=share_req.room,
        device_type=share_req.device_type,
    )

    share_req.status = DeviceShareRequest.Status.APPROVED
    share_req.resolved_at = timezone.now()
    share_req.save()

    messages.success(request, f"\"{share_req.device_name}\" isteği onaylandı. Cihaz {share_req.requester.username} kullanıcısına eklendi.")
    return redirect("smart_home:share_requests")


@login_required
@require_POST
def share_request_reject(request, request_id):
    share_req = get_object_or_404(
        DeviceShareRequest,
        pk=request_id,
        owner=request.user,
        status=DeviceShareRequest.Status.PENDING,
    )

    share_req.status = DeviceShareRequest.Status.REJECTED
    share_req.resolved_at = timezone.now()
    share_req.save()

    messages.success(request, f"\"{share_req.device_name}\" isteği reddedildi.")
    return redirect("smart_home:share_requests")
