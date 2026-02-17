import sys
import os
import json

# Add project to path
sys.path.append(r'c:\Users\hp\aivideogen')

# Mock Django settings
import unittest.mock as mock
from unittest.mock import MagicMock
sys.modules['django'] = MagicMock()
sys.modules['django.conf'] = MagicMock()
from django.conf import settings
settings.MEDIA_ROOT = r'c:\Users\hp\aivideogen\aivideogen\media'

import aivideogen.generator.avgl_engine as avgl_engine

json_path = r'c:\Users\hp\aivideogen\aivideogen\guiones\showcase_dynamic_v16.json'
with open(json_path, 'r', encoding='utf-8') as f:
    json_text = f.read()

script = avgl_engine.parse_avgl_json(json_text)

print(f"Script: {script.title}")
for b_idx, block in enumerate(script.blocks):
    print(f"Block {b_idx}: {block.title}")
    for s_idx, scene in enumerate(block.scenes):
        print(f"  Scene {s_idx}: {scene.title}")
        print(f"    Assets Count: {len(scene.assets)}")
        for a_idx, asset in enumerate(scene.assets):
            print(f"      Asset {a_idx}: {asset.type}")
