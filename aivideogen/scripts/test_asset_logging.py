
import os
import sys
import django
import json

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from generator.models import VideoProject
from generator.video_engine import generate_video_avgl
from generator.utils import ProjectLogger

def test_asset_logging():
    print("[INFO] Testing Verbose Asset Logging...")
    
    # 1. Create a dummy image file (absolute path)
    import tempfile
    from PIL import Image
    
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        img = Image.new('RGB', (100, 100), color = 'red')
        img.save(tmp.name)
        abs_image_path = tmp.name
    
    print(f"[INFO] Created dummy image at: {abs_image_path}")
    
    # 2. Setup Project with this asset
    scenes = [
        {
            "text": "Testing absolute path asset.",
            "assets": [{"id": abs_image_path, "type": abs_image_path, "provider": "local"}]
        },
        {
            "text": "Testing missing asset fallback.",
            "assets": [{"id": "non_existent_image.png", "type": "non_existent_image.png"}]
        }
    ]
    script = {
        "title": "Asset Test",
        "blocks": [{"scenes": scenes}]
    }
    
    project = VideoProject.objects.create(
        title="Asset Test Project",
        script_text=json.dumps(script),
        voice_id="es-DO-EmilioNeural"
    )
    
    # 3. Run Generation (limited)
    try:
        # We only need to see the logs for asset loading
        # The script will likely fail or finish quickly because it's only 2 scenes
        generate_video_avgl(project)
    except Exception as e:
        print(f"[ERROR] Engine Loop: {e}")
    finally:
        if os.path.exists(abs_image_path):
            os.remove(abs_image_path)
        
    # 4. Success check: We'll read the log_output from the project
    project.refresh_from_db()
    print("\n--- Project Logs ---")
    print(project.log_output)
    print("--------------------\n")
    
    if "✅ Ruta ABSOLUTA detectada y validada" in project.log_output:
        print("[SUCCESS] Found Absolute Path Validation log!")
    else:
        print("[FAILURE] Missing Absolute Path Validation log.")

if __name__ == "__main__":
    test_asset_logging()
