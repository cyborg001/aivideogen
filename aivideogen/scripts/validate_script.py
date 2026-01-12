import os
import django
import sys

# Setup Django
sys.path.append(r'c:\Users\Usuario\Documents\curso creacion contenido con ia\web_app2\web_app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.utils import validate_script_syntax
from generator.models import VideoProject

script_path = r'c:\Users\Usuario\Documents\curso creacion contenido con ia\articulos\guion_hitos_2026.md'

with open(script_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Mock project if none exists
p = VideoProject.objects.first()
if not p:
    print("Error: No VideoProject found in DB for validation context.")
    sys.exit(1)

is_valid, errors, duration, total_scenes = validate_script_syntax(text, p)

print(f"--- VALIDATION REPORT ---")
print(f"Valid: {is_valid}")
print(f"Duration: {int(duration // 60)}:{int(duration % 60):02d}")
print(f"Total Scenes: {total_scenes}")
print(f"Warnings/Errors: {len(errors)}")
for e in errors:
    print(f" - {e}")
