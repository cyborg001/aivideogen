import os
import django
import sys

# Add the project directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import Asset, VideoProject
import json

print("--- ASSETS SAMPLE ---")
for a in Asset.objects.all()[:5]:
    print(f"ID: {a.id}, File: {a.file.name}")

print("\n--- PROJECT SCRIPT SAMPLE (Asset paths) ---")
p = VideoProject.objects.order_by('-id').first()
if p:
    print(f"Project: {p.title}")
    data = json.loads(p.script_text)
    for b in data.get('blocks', [])[:1]:
        for s in b.get('scenes', [])[:2]:
            print(f"Scene: {s.get('title')}, Assets: {s.get('assets')}")
