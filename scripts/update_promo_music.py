
import os
import django
import sys
import json

# Setup django
sys.path.append(r'c:\Users\hp\aivideogen\aivideogen')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import VideoProject

# 1. Get Project 131
p = VideoProject.objects.get(id=131)
project_data = json.loads(p.script_text)

# 2. Add background music
project_data['background_music'] = "Frame-Dragging - The Grey Room _ Density & Time.mp3"
project_data['bg_music_volume'] = 0.20

# 3. Update DB
p.script_text = json.dumps(project_data, indent=4)
p.save()

print(f"Project 131 updated with music: {project_data['background_music']}")
