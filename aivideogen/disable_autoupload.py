
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import VideoProject
from datetime import timedelta
from django.utils import timezone

# Get projects created in the last hour
recent_time = timezone.now() - timedelta(hours=1)
projects = VideoProject.objects.filter(created_at__gte=recent_time, auto_upload_youtube=True)

print(f"Found {projects.count()} projects with auto-upload enabled.")

for p in projects:
    p.auto_upload_youtube = False
    p.save(update_fields=['auto_upload_youtube'])
    print(f"✅ Disabled auto-upload for Project {p.id}: {p.title}")
