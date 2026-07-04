import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User

username = 'Protas'
email = 'protasjunior254@gmail.com'
password = 'Protas@01'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superuser {username} created.')
else:
    print(f'Superuser {username} already exists.')
