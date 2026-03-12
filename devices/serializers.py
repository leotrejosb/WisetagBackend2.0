import json
from rest_framework import serializers
from .models import Device


class FormDataJSONField(serializers.JSONField):
    """Acepta JSON como string (desde FormData) o como objeto Python."""

    def to_internal_value(self, data):
        # QueryDict puede devolver lista con un string
        if isinstance(data, (list, tuple)) and len(data) == 1 and isinstance(data[0], str):
            data = data[0]
        if isinstance(data, str):
            if not data.strip() or data.strip() in ('undefined', 'null'):
                return []
            try:
                return json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return []
        return super().to_internal_value(data)


class DeviceSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()
    audio_url = serializers.SerializerMethodField()

    class Meta:
        model = Device
        fields = (
            'id', 'code', 'device_type', 'name', 'info',
            'photo', 'audio', 'photo_url', 'audio_url',
            'custom_fields', 'emergency_contacts', 'created_at', 'updated_at',
        )
        read_only_fields = ('code', 'created_at', 'updated_at')

    def get_photo_url(self, obj):
        if obj.photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return None

    def get_audio_url(self, obj):
        if obj.audio:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.audio.url)
            return obj.audio.url
        return None


class ActivateDeviceSerializer(serializers.Serializer):
    code = serializers.CharField()


class UpdateDeviceProfileSerializer(serializers.ModelSerializer):
    custom_fields = FormDataJSONField(required=False, allow_null=True)
    emergency_contacts = FormDataJSONField(required=False, allow_null=True)

    class Meta:
        model = Device
        fields = ('device_type', 'name', 'info', 'photo', 'audio', 'custom_fields', 'emergency_contacts')

    def validate_emergency_contacts(self, value):
        if value is None:
            # Actualización parcial sin contactos: mantener existentes
            if self.instance and self.instance.pk:
                return self.instance.emergency_contacts or []
            raise serializers.ValidationError('Debe agregar al menos un contacto de emergencia.')
        if isinstance(value, str):
            try:
                value = json.loads(value) if value.strip() else []
            except (json.JSONDecodeError, TypeError):
                value = []
        if not value or not isinstance(value, list):
            raise serializers.ValidationError('Debe agregar al menos un contacto de emergencia.')
        valid = [
            c for c in value
            if isinstance(c, dict) and str(c.get('phone', '')).strip() and str(c.get('relationship', '')).strip()
        ]
        if not valid:
            raise serializers.ValidationError(
                'Debe agregar al menos un contacto con número y parentesco.'
            )
        result = []
        for c in valid:
            result.append({
                'name': (c.get('name') or '').strip(),
                'phone': str(c.get('phone', '')).strip(),
                'relationship': str(c.get('relationship', '')).strip(),
            })
        return result
