import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from generator.models import VideoProject
print("Counting projects...")
count = VideoProject.objects.count()
print(f"Total projects: {count}")
