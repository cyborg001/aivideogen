
import os
import django
import sys
import json

# Setup django
sys.path.append(r'c:\Users\hp\aivideogen\aivideogen')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import VideoProject

# 1. Read the JSON v5 file
json_path = r'c:\Users\hp\aivideogen\aivideogen\guiones\cyborg001\promo_velo_gravitacional_v5.avgl.json'
with open(json_path, 'r', encoding='utf-8') as f:
    project_json = json.load(f)

# 2. Update DB Project 131
p = VideoProject.objects.get(id=131)
p.title = project_json['title']
p.script_text = json.dumps(project_json, indent=4)
p.save()

print(f"Project 131 upgraded to v5.0 Syntax. SFX are now structured. Title: {p.title}")
