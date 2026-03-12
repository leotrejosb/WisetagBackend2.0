"""
Crea el superadmin leo/leo para el panel de administración.
Uso: python manage.py create_superadmin
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea el superadmin con usuario leo y contraseña leo'

    def handle(self, *args, **options):
        email = 'leo@admin.com'
        password = 'leo'

        user, created = User.objects.get_or_create(
            email=email,
            defaults={'username': 'leo'},
        )
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Superadmin creado: email={email} / contraseña={password}'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Contraseña restablecida para {email}')
            )

        self.stdout.write(
            self.style.SUCCESS('Accede al admin en: http://127.0.0.1:8000/admin/')
        )
