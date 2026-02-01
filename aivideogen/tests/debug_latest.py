import os
import django
import sys
import json

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import VideoProject

try:
    # Get the LATEST project
    p = VideoProject.objects.last()
    print(f"Latest Project ID: {p.id}")
    print(f"Title: {p.title}")
    
    data = json.loads(p.script_text)
    
    for b_idx, block in enumerate(data.get('blocks', [])):
        for s_idx, scene in enumerate(block.get('scenes', [])):
            assets = scene.get('assets', [])
            if assets:
                for a in assets:
                    print(f"  SCENE {s_idx}: Asset='{a.get('type')}', Fit={a.get('fit')} (Type: {type(a.get('fit'))})")
            else:
                print(f"  SCENE {s_idx}: NO ASSETS")

except Exception as e:
    print(f"Error: {e}")
