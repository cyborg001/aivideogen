import os, django, json, sys
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from generator.models import VideoProject
from django.conf import settings
from moviepy import AudioFileClip

p = VideoProject.objects.get(id=170)
print(f"--- PROYECTO {p.id} ---")
print(f"Status: {p.status}")
# No imprimir todo el texto si es gigante
print(f"Texto (Script): {p.script_text[:200]}...")

ap = os.path.join(settings.MEDIA_ROOT, 'audio', f'project_{p.id}_scene_000.mp3')
print(f"Audio Path: {ap}")
if os.path.exists(ap):
    dur = AudioFileClip(ap).duration
    print(f"DURACION AUDIO: {dur}s")
else:
    print("AUDIO NO EXISTE")

# Ver el log buscando el texto recuperado real
if "Texto recuperado:" in p.log_output:
    idx = p.log_output.find("Texto recuperado:")
    print(f"LOG FRAGMENT: {p.log_output[idx:idx+300]}")
