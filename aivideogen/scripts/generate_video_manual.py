
import os
import sys
import django
import json
print("Script starting...", flush=True)

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aivideogen.config.settings')
django.setup()

from generator.models import VideoProject, Asset
from generator.video_engine import generate_video_avgl

def generate_tesla_video():
    print("--- Converting Tesla Script to Video ---")
    
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'guiones', 'tesla_model_pi.json')
    
    with open(json_path, 'r', encoding='utf-8') as f:
        script_data = json.load(f)
        
    script_text = json.dumps(script_data, indent=4)
    print(f"Loaded script: {script_data.get('title')}")

    # Create distinct project for test
    project, created = VideoProject.objects.get_or_create(
        title="Test: Tesla Model Pi (Manual)",
        defaults={
            'script_text': script_text,
            'aspect_ratio': 'portrait', # As per JSON cues usually, or default
            'engine': 'edge'
        }
    )
    
    # Always update script text in case JSON changed
    project.script_text = script_text
    project.aspect_ratio = 'portrait' 
    project.save()
    
    print(f"Project ID: {project.id}")
    print("Starting generation...")
    
    generate_video_avgl(project)
    
    if project.output_video:
        print(f"SUCCESS: Video generated at {project.output_video.path}")
    else:
        print("FAIL: Video file not set in project.")

if __name__ == "__main__":
    generate_tesla_video()
