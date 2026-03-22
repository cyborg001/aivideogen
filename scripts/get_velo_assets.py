
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

# List unique asset IDs from the script
assets = set()
for block in content.get('blocks', []):
    for scene in block.get('scenes', []):
        for asset in scene.get('assets', []):
            assets.add(asset.get('id'))

print(f"Project ID: {p.id}")
print(f"Total Unique Assets: {len(assets)}")
print("Assets List:")
for asset in sorted(list(assets)):
    print(f"- {asset}")
