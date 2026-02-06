import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from generator.models import VideoProject

p = VideoProject.objects.get(id=17)
print(f"Project ID: {p.id}")
print(f"Title: {p.title}")
print(f"Status: {p.status}")
print(f"Progress: {p.progress_total}")
print(f"Video Path: {p.output_video.path if p.output_video else 'No video'}")

if p.output_video and os.path.exists(p.output_video.path):
    print(f"Video Size: {os.path.getsize(p.output_video.path)} bytes")
else:
    print("Video file NOT found in disk.")

with open('project_17_debug.log', 'w', encoding='utf-8') as f:
    f.write(p.log_output)
print("Logs saved to project_17_debug.log")
