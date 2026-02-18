
import os
import sys
import django
from django.conf import settings

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aivideogen.settings')
django.setup()

from generator.models import VideoProject

latest_project = VideoProject.objects.last()
if latest_project:
    print(f"Latest Project ID: {latest_project.id}")
    print(f"Title: {latest_project.title}")
    print(f"Engine: '{latest_project.engine}'") # Quotes to see empty string
else:
    print("No projects found.")
