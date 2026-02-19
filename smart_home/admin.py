from django.contrib import admin

from .models import SmartDevice


@admin.register(SmartDevice)
class SmartDeviceAdmin(admin.ModelAdmin):
    """Admin panelinde cihaz yönetimi."""

    list_display = (
        "name",
        "room",
        "device_type",
        "ip_address",
        "is_active",
        "last_seen",
    )
    list_filter = ("room", "device_type", "is_active")
    search_fields = ("name", "ip_address")
    list_editable = ("is_active",)
    readonly_fields = ("created_at", "updated_at", "last_seen")
