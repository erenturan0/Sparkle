from django.conf import settings
from django.db import models


class SmartDevice(models.Model):

    class DeviceType(models.TextChoices):
        SWITCH = "switch", "Anahtar / Röle"
        LIGHT = "light", "Aydınlatma"
        PLUG = "plug", "Akıllı Priz"
        SENSOR = "sensor", "Sensör"

    class Room(models.TextChoices):
        LIVING_ROOM = "salon", "Salon"
        BEDROOM = "yatak_odasi", "Yatak Odası"
        KITCHEN = "mutfak", "Mutfak"
        BATHROOM = "banyo", "Banyo"
        HALLWAY = "koridor", "Koridor"
        BALCONY = "balkon", "Balkon"
        OFFICE = "ofis", "Çalışma Odası"
        OTHER = "diger", "Diğer"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Sahip",
        related_name="devices",
    )
    name = models.CharField(
        "Cihaz Adı",
        max_length=100,
        help_text="Örn: Salon Lambası, Mutfak Prizi",
    )
    ip_address = models.GenericIPAddressField(
        "IP Adresi",
        protocol="IPv4",
        help_text="Tasmota cihazın yerel IP adresi",
    )
    room = models.CharField(
        "Oda",
        max_length=50,
        choices=Room.choices,
        default=Room.LIVING_ROOM,
    )
    device_type = models.CharField(
        "Cihaz Tipi",
        max_length=20,
        choices=DeviceType.choices,
        default=DeviceType.SWITCH,
    )
    is_active = models.BooleanField(
        "Aktif",
        default=True,
        help_text="Cihaz sisteme dahil mi?",
    )
    last_seen = models.DateTimeField(
        "Son Görülme",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField("Oluşturulma", auto_now_add=True)
    updated_at = models.DateTimeField("Güncellenme", auto_now=True)

    class Meta:
        verbose_name = "Akıllı Cihaz"
        verbose_name_plural = "Akıllı Cihazlar"
        ordering = ["room", "name"]
        unique_together = [("owner", "ip_address")]

    def __str__(self):
        return f"{self.get_room_display()} – {self.name}"

    @property
    def tasmota_base_url(self):
        return f"http://{self.ip_address}/cm"


class DeviceShareRequest(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Bekliyor"
        APPROVED = "approved", "Onaylandı"
        REJECTED = "rejected", "Reddedildi"

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="İsteyen",
        related_name="sent_share_requests",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Cihaz Sahibi",
        related_name="received_share_requests",
    )
    ip_address = models.GenericIPAddressField(
        "IP Adresi",
        protocol="IPv4",
    )
    device_name = models.CharField("Cihaz Adı", max_length=100)
    room = models.CharField("Oda", max_length=50)
    device_type = models.CharField("Cihaz Tipi", max_length=20)
    status = models.CharField(
        "Durum",
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField("Oluşturulma", auto_now_add=True)
    resolved_at = models.DateTimeField("Sonuçlanma", null=True, blank=True)

    class Meta:
        verbose_name = "Cihaz Paylaşım İsteği"
        verbose_name_plural = "Cihaz Paylaşım İstekleri"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.requester.username} → {self.owner.username}: {self.ip_address}"
