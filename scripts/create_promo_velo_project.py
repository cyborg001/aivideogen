
import os
import django
import sys
import json

# Setup django
sys.path.append(r'c:\Users\hp\aivideogen\aivideogen')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import VideoProject
from generator.avgl_engine import convert_text_to_avgl_json

# 1. Read the AVGL text
avgl_path = r'c:\Users\hp\aivideogen\aivideogen\guiones\cyborg001\promo_velo_gravitacional.avgl.txt'
with open(avgl_path, 'r', encoding='utf-8') as f:
    avgl_text = f.read()

# 2. Convert to JSON format (VideoProject format)
# Note: convert_text_to_avgl_json returns the full project structure
project_data = convert_text_to_avgl_json(avgl_text)

# Set some project metadata
project_data['title'] = "PROMO: El Velo Gravitacional - Prólogo"
project_data['voice'] = "es-ES-AlvaroNeural" # El Arquitecto usa a Alvaro usualmente
project_data['aspect_ratio'] = "portrait" # Es un Short/Promo

# 3. Create VideoProject record
new_project = VideoProject.objects.create(
    title=project_data['title'],
    script_text=json.dumps(project_data, indent=4),
    aspect_ratio=project_data['aspect_ratio'],
    voice_id=project_data['voice']
)

print(f"Project created with ID: {new_project.id} | Title: {new_project.title}")
