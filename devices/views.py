import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Device

logger = logging.getLogger(__name__)
from .serializers import (
    ActivateDeviceSerializer,
    DeviceSerializer,
    UpdateDeviceProfileSerializer,
)


# Código de prueba que se puede activar ilimitadas veces
TEST_CODE = '123'


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def activate(request):
    """Valida el código y activa/vincula el dispositivo al usuario."""
    serializer = ActivateDeviceSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    code = serializer.validated_data['code'].strip()

    # Código de prueba 123 - crear nuevo dispositivo cada vez (para ensayos)
    if code == TEST_CODE:
        device = Device.objects.create(
            code=TEST_CODE,
            user=request.user,
            device_type='pet',
        )
        return Response(DeviceSerializer(device, context={'request': request}).data, status=status.HTTP_201_CREATED)

    # Códigos reales - buscar dispositivo existente
    try:
        device = Device.objects.get(code=code, user=request.user)
        return Response(DeviceSerializer(device, context={'request': request}).data, status=status.HTTP_200_OK)
    except Device.DoesNotExist:
        pass
    try:
        device = Device.objects.get(code=code, user__isnull=True)
        device.user = request.user
        device.save()
        return Response(DeviceSerializer(device, context={'request': request}).data, status=status.HTTP_200_OK)
    except Device.DoesNotExist:
        return Response(
            {'detail': 'Código de dispositivo no válido.'},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_devices(request):
    """Lista los dispositivos del usuario."""
    devices = Device.objects.filter(user=request.user)
    return Response(DeviceSerializer(devices, many=True, context={'request': request}).data)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def device_detail(request, pk):
    """Obtener o actualizar perfil NFC del dispositivo."""
    try:
        device = Device.objects.get(pk=pk, user=request.user)
    except Device.DoesNotExist:
        return Response(
            {'detail': 'Dispositivo no encontrado.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == 'GET':
        return Response(DeviceSerializer(device, context={'request': request}).data)

    if request.method == 'PATCH':
        serializer = UpdateDeviceProfileSerializer(
            device,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            serializer.save()
            return Response(DeviceSerializer(device, context={'request': request}).data)
        logger.warning("PATCH device %s validation failed: %s | data keys: %s", pk, serializer.errors, list(request.data.keys()))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
