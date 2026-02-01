import os
import sys
import django
import json

# Setup Django Environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.avgl_engine import parse_avgl_json

json_content = """
{
    "title": "Test Group Parsing",
    "blocks": [
        {
            "title": "Block with Groups",
            "groups": [
                {
                    "master_asset": {
                        "type": "image.png",
                        "zoom": "1.0:1.3"
                    },
                    "scenes": [
                        {
                            "title": "Scene Inside Group",
                            "text": "This scene should inherit the image."
                        },
                        {
                            "title": "Scene With Override",
                            "text": "This scene has its own asset.",
                            "assets": [{"type": "override.png"}]
                        }
                    ]
                }
            ]
        }
    ]
}
"""

print("Testing parse_avgl_json with groups...")
script = parse_avgl_json(json_content)

print(f"Script Title: {script.title}")
for block in script.blocks:
    print(f"Block: {block.title}")
    print(f"Total Scenes: {len(block.scenes)}")
    for i, scene in enumerate(block.scenes):
        print(f"  Scene {i+1}: {scene.title}")
        print(f"  Text: {scene.text}")
        if scene.assets:
            asset = scene.assets[0]
            print(f"  Asset: {asset.type} (Zoom: {asset.zoom})")
        else:
            print("  Asset: None")

if len(script.blocks[0].scenes) == 2:
    print("✅ SUCCESS: 2 scenes found in group!")
else:
    print("❌ FAILURE: Incorrect number of scenes found.")
