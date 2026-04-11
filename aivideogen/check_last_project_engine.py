
import os
import sys
import django
from django.conf import settings

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aivideogen.settings')
django.setup()



from generator.models import VideoProject

project = VideoProject.objects.last()
if project:
    print(f"ID: {project.id} | Title: {project.title}")
    print("--- SCRIPT TEXT ---")
    print(project.script_text)
    print("--- END SCRIPT TEXT ---")
else:
    print("No projects found.")

