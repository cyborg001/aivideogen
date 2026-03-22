import os
import django
import json
import sys

# Setup Django
sys.path.append(r'c:\Users\hp\aivideogen\aivideogen')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import VideoProject
from generator.video_engine import generate_video_avgl
import threading

# 1. Definir Guion: Video + LipSync + No Text
script_data = {
  "title": "Prueba Fuego v5.2: Auto-LipSync",
  "language": "es",
  "dubbing_mode": "lipsync",
  "blocks": [
    {
      "scenes": [
        {
          "title": "Trump Auto-LipSync",
          "text": "", # Activa Auto-Dubbing
          "assets": [
            {
              "id": "white_house_dinner_japan.mp4",
              "start_time": 0.0,
              "end_time": 5.0
            }
          ]
        }
      ]
    }
  ]
}

# 2. Crear Proyecto
project = VideoProject.objects.create(
    title="TEST_AUTO_LIPSYNC_V52",
    script_text=json.dumps(script_data),
    aspect_ratio='landscape',
    engine='edge',
    status='pending',
    dubbing_mode='lipsync',
    language='es'
)

print(f"Proyecto Creado: ID {project.id}")

# 3. Lanzar motor
print("Iniciando Prueba de Fuego (v5.2 + LipSync)...")
try:
    generate_video_avgl(project)
    print(f"Fin del proceso. Status: {project.status}")
except Exception as e:
    print(f"Error Crítico: {e}")
