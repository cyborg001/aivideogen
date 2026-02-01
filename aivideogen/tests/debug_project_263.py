import os
import django
import sys
import json

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import VideoProject

try:
    p = VideoProject.objects.get(id=263)
    data = json.loads(p.script_text)
    
    print(f"Project: {p.title} (ID: 263)")
    for b_idx, block in enumerate(data.get('blocks', [])):
        print(f"BLOCK {b_idx}: {block.get('title')}")
        for s_idx, scene in enumerate(block.get('scenes', [])):
            assets = scene.get('assets', [])
            if assets:
                for a in assets:
                    print(f"  SCENE {s_idx} ('{scene.get('title')}'): Asset='{a.get('type')}', Fit={a.get('fit')}")
            else:
                print(f"  SCENE {s_idx} ('{scene.get('title')}'): NO ASSETS")

except Exception as e:
    print(f"Error: {e}")
