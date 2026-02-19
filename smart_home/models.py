from django.db import models


class SmartDevice(models.Model):
    """Tasmota firmware'li akıllı cihazları temsil eden model."""

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

    # ── Temel Bilgiler ──────────────────────────────────────
    name = models.CharField(
        "Cihaz Adı",
        max_length=100,
        help_text="Örn: Salon Lambası, Mutfak Prizi",
    )
    ip_address = models.GenericIPAddressField(
        "IP Adresi",
        protocol="IPv4",
        unique=True,
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

    # ── Durum Bilgileri ─────────────────────────────────────
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

    # ── Zaman Damgaları ─────────────────────────────────────
    created_at = models.DateTimeField("Oluşturulma", auto_now_add=True)
    updated_at = models.DateTimeField("Güncellenme", auto_now=True)

    class Meta:
        verbose_name = "Akıllı Cihaz"
        verbose_name_plural = "Akıllı Cihazlar"
        ordering = ["room", "name"]

    def __str__(self):
        return f"{self.get_room_display()} – {self.name}"

    @property
    def tasmota_base_url(self):
        """Tasmota HTTP API temel URL'ini döndürür."""
        return f"http://{self.ip_address}/cm"
