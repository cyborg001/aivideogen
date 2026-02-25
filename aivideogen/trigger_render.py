import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import VideoProject
from generator.utils import generate_video_process

if len(sys.argv) < 2:
    print("Uso: python trigger_render.py <project_id>")
    sys.exit(1)

project_id = sys.argv[1]
try:
    project = VideoProject.objects.get(id=project_id)
    print(f"Iniciando renderizado para Proyecto {project.id}: {project.title}")
    generate_video_process(project)
    print(f"Proceso finalizado para Proyecto {project.id}")
except VideoProject.DoesNotExist:
    print(f"El proyecto con ID {project_id} no existe.")
except Exception as e:
    print(f"Error durante el renderizado: {e}")
