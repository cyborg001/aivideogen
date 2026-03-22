
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

# 1. Read the newest AVGL text (v5 - 100% Consistent)
avgl_path = r'c:\Users\hp\aivideogen\aivideogen\guiones\cyborg001\promo_velo_gravitacional_v5.avgl.txt'
with open(avgl_path, 'r', encoding='utf-8') as f:
    avgl_text = f.read()

# 2. Convert to JSON format
project_data = convert_text_to_avgl_json(avgl_text)

# Set metadata and music
project_data['title'] = "PROMO: El Velo Gravitacional (Consistencia 100%)"
project_data['voice'] = "es-ES-AlvaroNeural"
project_data['aspect_ratio'] = "portrait"
project_data['background_music'] = "Frame-Dragging - The Grey Room _ Density & Time.mp3"
project_data['bg_music_volume'] = 0.20

# 3. Update Existing Project 131
p = VideoProject.objects.get(id=131)
p.title = project_data['title']
p.script_text = json.dumps(project_data, indent=4)
p.save()

print(f"Project 131 updated with 100% original assets. Title: {p.title}")
