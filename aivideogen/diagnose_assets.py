import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aivideogen.settings')
import sys
sys.path.append('.')
django.setup()

from generator.models import VideoProject

p = VideoProject.objects.get(id=37)
script = json.loads(p.script_text)

print("--- MAPPING SCRIPT ASSETS ---")
global_idx = 0
for b_idx, block in enumerate(script.get('blocks', [])):
    print(f"Block {b_idx+1}: {block.get('title')}")
    for s_idx, scene in enumerate(block.get('scenes', [])):
        global_idx += 1
        assets = scene.get('assets', [])
        if assets:
            a = assets[0]
            a_id = a.get('id') or a.get('type')
            print(f"  Item {global_idx} (Scene {b_idx+1}.{s_idx+1}): {a_id}")
        else:
            print(f"  Item {global_idx} (Scene {b_idx+1}.{s_idx+1}): NO ASSET")

print("\n--- ANALYZING LOGS ---")
logs = p.log_output.split('\n')
for line in logs:
    if "Asset encontrado" in line or "Asset NO encontrado" in line or "Respaldo" in line:
        print(line.strip())
