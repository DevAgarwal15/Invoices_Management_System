import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()

print('superuser_count', User.objects.filter(is_superuser=True).count())
print('staff_count', User.objects.filter(is_staff=True).count())
print('total_users', User.objects.count())
