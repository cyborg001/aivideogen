
import os
import django
import sys

# Setup django
sys.path.append(r'c:\Users\hp\aivideogen\aivideogen')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import VideoProject

# Get the most recent project with "Velo" or "Regalo" in title or most recent 5
projects = VideoProject.objects.filter(title__icontains='Velo') | VideoProject.objects.filter(title__icontains='Regalo')

if not projects.exists():
    projects = VideoProject.objects.order_by('-id')[:5]

for p in projects:
    print(f"ID: {p.id} | Title: {p.title}")
    # Print a bit of the script to see the assets
    if p.script_text:
        print(f"Script Snippet: {p.script_text[:100]}...")
    print("-" * 20)
