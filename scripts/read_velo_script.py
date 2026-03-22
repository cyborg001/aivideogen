
import os
import django
import sys
import json

# Setup django
sys.path.append(r'c:\Users\hp\aivideogen\aivideogen')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import VideoProject

p = VideoProject.objects.get(id=123)
content = json.loads(p.script_text)

# Print scenes and their text
print(f"TITLE: {p.title}")
for block in content.get('blocks', []):
    for i, scene in enumerate(block.get('scenes', [])):
        print(f"Scene {i+1}: {scene.get('text')}")
        print("-" * 10)
