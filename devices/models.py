from django.conf import settings
from django.db import models


class Device(models.Model):
    TYPE_CHOICES = [
        ('pet', 'WISETAG Pet'),
        ('band', 'WISETAG Band'),
    ]

    code = models.CharField(max_length=50)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='devices',
        null=True,
        blank=True,
    )
    device_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='pet')
    name = models.CharField(max_length=100, blank=True)
    info = models.TextField(blank=True)
    photo = models.ImageField(upload_to='devices/photos/', blank=True, null=True)
    audio = models.FileField(upload_to='devices/audio/', blank=True, null=True)
    # Campos personalizados: [{"label": "RUT", "value": "99.999.999", "important": true}, ...]
    custom_fields = models.JSONField(default=list, blank=True)
    # Contactos de emergencia obligatorios: [{"name": "Ana C.", "phone": "+56912345678", "relationship": "Madre"}, ...]
    emergency_contacts = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_device_type_display()} - {self.code}"
