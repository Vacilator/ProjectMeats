from django.contrib.auth.models import User
from apps.core.models import UserProfile

# Create superuser
if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser(
        'admin',
        'admin@example.com',
        'ProjectMeats2024!'
    )
    # Create profile
    UserProfile.objects.get_or_create(user=user)
    print('Admin user created successfully')
else:
    print('Admin user already exists')
