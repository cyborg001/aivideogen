
import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aivideogen.settings')
django.setup()

from generator.models import VideoProject

projects = VideoProject.objects.all().order_by('-created_at')[:20]
print("ID|Title|Status|Date")
for p in projects:
    print(f"{p.id}|{p.title}|{p.status}|{p.created_at.strftime('%Y-%m-%d')}")
