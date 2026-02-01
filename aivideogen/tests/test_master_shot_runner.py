import os
import sys
import django
import json

# Setup Django Environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import VideoProject
from generator.video_engine import generate_video_avgl

# Path to test JSON
json_path = r"c:\Users\Usuario\Documents\curso creacion contenido con ia\test_master_shot.json"

if not os.path.exists(json_path):
    print(f"ERROR: File not found: {json_path}")
    sys.exit(1)

with open(json_path, 'r', encoding='utf-8') as f:
    script_content = f.read()

print("Creating Test Project...")
# Create dummy project
project = VideoProject.objects.create(
    title="Test Master Shot Run",
    script_text=script_content,
    voice_id="es-ES-AlvaroNeural",
    engine="edge"
)

print(f"Project created with ID: {project.id}")
print("Starting Generation...")

try:
    generate_video_avgl(project)
    print("Generation Logic Completed.")
    
    # Check Result
    project.refresh_from_db()
    print(f"Final Status: {project.status}")
    if project.video_file:
        print(f"Video File: {project.video_file.path}")
    else:
        print("No video file generated.")
        
except Exception as e:
    print(f"EXCEPTION: {e}")
    import traceback
    traceback.print_exc()
