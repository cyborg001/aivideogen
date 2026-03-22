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

script_path = r'c:\Users\hp\aivideogen\aivideogen\guiones\white_house_japan_summit_2026.json'

with open(script_path, 'r', encoding='utf-8') as f:
    script_data = json.load(f)

# Create Project
project = VideoProject.objects.create(
    title=script_data.get('title', 'Cyborg Video'),
    script_text=json.dumps(script_data, ensure_ascii=False),
    language=script_data.get('language', 'es'),
    dubbing_mode=script_data.get('dubbing_mode', 'hq'),
    music_volume=script_data.get('music_volume', 0.15),
    status='pending'
)

print(f"Proyecto registrado con ID: {project.id}")

# Trigger Render
print(f"Iniciando renderizado para {project.title}...")
try:
    generate_video_process(project)
    print("Renderizado completado exitosamente.")
    project.refresh_from_db()
    if project.output_video:
        print(f"Video generado en: {project.output_video.path}")
except Exception as e:
    print(f"Error durante el renderizado: {e}")
