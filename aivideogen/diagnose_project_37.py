import os
import sys
import django
import re

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aivideogen.settings')
django.setup()

from generator.models import VideoProject

p = VideoProject.objects.get(id=37)
logs = p.log_output.split('\n')

current_item = "Global"
results = []

for line in logs:
    if "Escena" in line and "/" in line and ":" in line:
        current_item = line.strip()
    
    if "Asset encontrado" in line or "Asset NO encontrado" in line or "Respaldo" in line:
        results.append(f"{current_item} -> {line.strip()}")

with open('diagnose_results.txt', 'w', encoding='utf-8') as f:
    for r in results:
        f.write(r + '\n')
