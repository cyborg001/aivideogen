import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from generator.models import VideoProject

print("Ultimos 10 proyectos:")
for p in VideoProject.objects.all().order_by('-id')[:10]:
    print(f"ID: {p.id} | Title: {p.title} | Status: {p.status} | Progress: {p.progress_total}")
