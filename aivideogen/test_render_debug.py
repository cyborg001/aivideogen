import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import VideoProject
from generator.video_engine import generate_video_avgl
import json

def test_engine():
    # Create a dummy project
    project = VideoProject.objects.create(
        title="Test Engine Debug",
        script_text='{"blocks": [{"title": "Test", "scenes": [{"title": "Scene 1", "text": "Test narration.", "assets": [{"type": "assets/notiaci_intro_wide.png"}]}]}]}',
        engine='edge',
        status='pending'
    )
    
    print(f"Project created with ID: {project.id}")
    
    try:
        generate_video_avgl(project)
        print("Render finished.")
        
        # Check file
        video_path = f"c:/Users/hp/aivideogen/aivideogen/media/videos/project_{project.id}.mp4"
        if os.path.exists(video_path):
            from moviepy import VideoFileClip
            clip = VideoFileClip(video_path)
            print(f"Generated Duration: {clip.duration}")
            clip.close()
        else:
            print(f"Video file NOT found: {video_path}")
            
    except Exception as e:
        print(f"Error during render: {e}")
    finally:
        # Clean up DB
        # project.delete()
        pass

if __name__ == "__main__":
    test_engine()
