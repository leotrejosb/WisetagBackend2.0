from django.contrib import admin
from .models import Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('code', 'user', 'device_type', 'name', 'created_at')
    list_filter = ('device_type',)
    search_fields = ('code', 'name', 'user__email')
