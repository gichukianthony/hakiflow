from django.contrib.auth.models import User
u = User.objects.get(username='admin')
u.set_password('password123')
u.save()
print('Password set for admin')
