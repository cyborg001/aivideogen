import os, django, json, sys
sys.path.append(r'c:\Users\hp\aivideogen\aivideogen')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from generator.models import VideoProject
from generator.video_engine import generate_video_avgl

# 1. Guion Ultra Corto (2s)
script_data = {
  "title": "Verificacion Final Bill v5.2",
  "language": "es",
  "dubbing_mode": "lipsync",
  "blocks": [
    {
      "scenes": [
        {
          "title": "Trump 2s Auto",
          "text": "", 
          "assets": [
            {
              "id": "white_house_dinner_japan.mp4",
              "start_time": 25.0,
              "end_time": 30.0
            }
          ]
        }
      ]
    }
  ]
}

# 2. Crear Proyecto
project = VideoProject.objects.create(
    title="CERTIFICACION_V52_LIPSYNC",
    script_text=json.dumps(script_data),
    aspect_ratio='landscape',
    engine='edge',
    status='pending',
    dubbing_mode='lipsync',
    language='es'
)

print(f"Proyecto Creado: ID {project.id}")

# 3. Lanzar motor
print("Iniciando Certificacion Final...")
try:
    generate_video_avgl(project)
    print(f"Fin del proceso. Status: {project.status}")
except Exception as e:
    print(f"Error Crítico: {e}")
