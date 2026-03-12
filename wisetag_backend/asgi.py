"""
ASGI config for wisetag_backend project.
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wisetag_backend.settings')

application = get_asgi_application()
