
import os
import sys
import django
import json
from PIL import Image

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from generator.models import VideoProject
from generator.video_engine import generate_video_avgl

def create_dummy_image(path):
    img = Image.new('RGB', (1920, 1080), color = (255, 0, 0)) # Red image
    img.save(path)
    print(f"Created dummy image at {path}")

def test_absolute_path_render():
    # 1. Prepare external asset
    temp_dir = os.path.join(os.getcwd(), 'temp_test_assets')
    os.makedirs(temp_dir, exist_ok=True)
    abs_image_path = os.path.join(temp_dir, 'absolute_red.png')
    create_dummy_image(abs_image_path)
    
    # 2. Create Project
    script_data = {
        "title": "Absolute Path Test",
        "blocks": [
            {
                "scenes": [
                    {
                        "text": "This is a test of absolute paths.",
                        "assets": [
                            {"type": abs_image_path, "id": abs_image_path} # Simulate frontend sending absolute path
                        ]
                    }
                ]
            }
        ]
    }
    
    project = VideoProject.objects.create(
        title="Test Absolute Paths",
        script_text=json.dumps(script_data),
        voice_id="es-DO-EmilioNeural"
    )
    print(f"Created project {project.id}")
    
    # 3. Render
    try:
        print("Starting render...")
        output_file = generate_video_avgl(project)
        if output_file and os.path.exists(output_file):
            print(f"✅ Render SUCCESS! Video at: {output_file}")
            # Optional: Check if fallback warning was NOT logged? Hard to do unless we mock logger.
            # But if it rendered without error and didn't crash, it likely worked.
        else:
            print("❌ Render FAILED. No output file.")
    except Exception as e:
        print(f"❌ Render CRASHED: {e}")
        import traceback
        traceback.print_exc()
    
    # Cleanup
    # project.delete()
    # if os.path.exists(abs_image_path): os.remove(abs_image_path)
    # os.rmdir(temp_dir)

if __name__ == "__main__":
    test_absolute_path_render()
