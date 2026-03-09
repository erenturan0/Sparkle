from django.contrib import admin

from .models import SmartDevice, DeviceShareRequest


@admin.register(SmartDevice)
class SmartDeviceAdmin(admin.ModelAdmin):

    list_display = (
        "owner",
        "name",
        "room",
        "device_type",
        "ip_address",
        "is_active",
        "last_seen",
    )
    list_filter = ("owner", "room", "device_type", "is_active")
    search_fields = ("name", "ip_address")
    list_editable = ("is_active",)
    readonly_fields = ("created_at", "updated_at", "last_seen")


@admin.register(DeviceShareRequest)
class DeviceShareRequestAdmin(admin.ModelAdmin):

    list_display = ("requester", "owner", "ip_address", "device_name", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("requester__username", "owner__username", "ip_address")
    readonly_fields = ("created_at", "resolved_at")
