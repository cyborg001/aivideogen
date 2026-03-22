import os
import django
import json
import sys

# Setup Django
sys.path.append(r'c:\Users\hp\aivideogen\aivideogen')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import VideoProject
from generator.utils import generate_video_process
import threading

# 1. Definir Guion de Prueba (Sin Texto, Dubbing HQ)
script_data = {
  "title": "Test Traduccion Directa v5.2",
  "language": "es",
  "dubbing_mode": "hq",
  "blocks": [
    {
      "title": "Prueba",
      "scenes": [
        {
          "title": "Bilateral Trump-Japan (Auto)",
          "text": "",  # DEBE ESTAR VACÍO PARA ACTIVAR AUTO-DUBBING
          "assets": [
            {
              "id": "white_house_dinner_japan.mp4",
              "start_time": 0.0,
              "end_time": 15.0
            }
          ]
        }
      ]
    }
  ]
}

# 2. Crear Proyecto
project = VideoProject.objects.create(
    title="Test Auto-Dubbing v5.2",
    script_text=json.dumps(script_data),
    aspect_ratio='landscape',
    engine='edge',
    status='pending',
    dubbing_mode='hq',
    language='es'
)

print(f"Proyecto Creado: ID {project.id}")

# 3. Lanzar motor
print("Iniciando motor v5.2...")
generate_video_process(project)

print(f"Fin del proceso. Status: {project.status}")
print(f"Log: {project.log_output[-500:]}")
