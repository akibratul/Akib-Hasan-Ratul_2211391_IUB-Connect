import os, django, json
os.environ['DJANGO_SETTINGS_MODULE'] = 'iubconnect.settings'
django.setup()
from core.models import User, StudentProfile, AlumniProfile

# Create admin
if not User.objects.filter(email='admin@iub.edu.bd').exists():
    admin = User.objects.create_superuser(username='admin@iub.edu.bd', email='admin@iub.edu.bd', password='admin123', first_name='Admin', role='admin')
    print('Admin created: admin@iub.edu.bd / admin123')

# Create student
if not User.objects.filter(email='2211391@iub.edu.bd').exists():
    s = User.objects.create_user(username='2211391@iub.edu.bd', email='2211391@iub.edu.bd', password='student123', first_name='Akib', last_name='Ratul', role='student')
    StudentProfile.objects.create(user=s, department='CSE', year=3, skills=json.dumps(['Python', 'React', 'SQL']), interests='AI, Web Development')
    print('Student created: 2211391@iub.edu.bd / student123')

# Create alumni
if not User.objects.filter(email='abdullah@gmail.com').exists():
    a = User.objects.create_user(username='abdullah@gmail.com', email='abdullah@gmail.com', password='alumni123', first_name='Abdullah', role='alumni')
    AlumniProfile.objects.create(user=a, graduation_year=2017, profession='Web Developer')
    print('Alumni created: abdullah@gmail.com / alumni123')

print('Seed complete!')
