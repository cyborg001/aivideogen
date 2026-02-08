
import os
import sys
import django
import time
import threading
import json

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from generator.models import VideoProject
from generator.video_engine import generate_video_avgl
from django.core.cache import cache

def monitor_cache(project_id, stop_event):
    print("[INFO] Starting Cache Monitor...")
    while not stop_event.is_set():
        p_val = cache.get(f"project_{project_id}_progress")
        s_text = cache.get(f"project_{project_id}_status_text")
        if p_val or s_text:
            print(f"   Cache Report: {p_val:.1f}% | {s_text}")
        time.sleep(0.5)

def test_progress_logging():
    print("[INFO] Testing Granular Progress Logging...")
    
    # 1. Create Multi-Scene Project
    scenes = [{"text": f"Scene {i}", "assets": []} for i in range(20)]
    script = {
        "title": "Progress Test",
        "blocks": [{"scenes": scenes}]
    }
    
    project = VideoProject.objects.create(
        title="Progress Test Project",
        script_text=json.dumps(script),
        voice_id="es-DO-EmilioNeural"
    )
    
    # 2. Initialize Control Variables
    stop_event = threading.Event()
    monitor_thread = threading.Thread(target=monitor_cache, args=(project.id, stop_event))
    monitor_thread.start()
    
    # 3. Run Generation
    try:
        generate_video_avgl(project)
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    finally:
        stop_event.set()
        monitor_thread.join()
        
    # 4. Verify Final State
    project.refresh_from_db()
    print(f"[DONE] Final DB Status: {project.status}")
    print(f"[DONE] Final DB Progress: {project.progress}%")

if __name__ == "__main__":
    test_progress_logging()
