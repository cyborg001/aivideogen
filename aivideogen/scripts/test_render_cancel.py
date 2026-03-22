import os
import sys
import django
import threading
import time

# Add base directory to path
BASE_DIR = r'c:\Users\hp\aivideogen\aivideogen'
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Setup Django - Using 'config.settings' as seen in manage.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import VideoProject
from generator.video_engine import generate_video_avgl

def simulate_cancellation(project_id):
    time.sleep(15) # Wait for render to start and process some scenes
    print(f"--- SIMULATING CANCEL for Project {project_id} ---")
    project = VideoProject.objects.get(id=project_id)
    project.status = 'cancel'
    # Use direct SQL update to avoid issues with Django's internal state if needed, 
    # but .save() should be fine since the engine uses .refresh_from_db()
    project.save(update_fields=['status'])
    print("--- Status set to 'cancel' in DB ---")

def test_cancel():
    # Get the last Genghis project as a template
    original = VideoProject.objects.filter(title__icontains='Genghis Khan - Acto 2').last()
    if not original:
        print("No Genghis project found to test.")
        return

    # Create a clone for testing
    import json
    test_p = VideoProject.objects.create(
        title="TEST CANCEL PROJECT",
        script_text=original.script_text,
        engine='edge',
        aspect_ratio='landscape',
        render_mode='cpu'
    )
    
    print(f"Created Test Project ID: {test_p.id}")

    # Start cancellation thread
    cancel_thread = threading.Thread(target=simulate_cancellation, args=(test_p.id,))
    cancel_thread.start()

    # Start render (this is blocking)
    print("Starting render...")
    try:
        generate_video_avgl(test_p)
        print("Render function call returned.")
    except Exception as e:
        print(f"Render crashed/stopped: {e}")

    test_p.refresh_from_db()
    print(f"Final Project Status: {test_p.status}")
    if test_p.status == 'cancel':
        print("SUCCESS: Render stopped on cancellation.")
    else:
        print("FAILURE: Render did not stop or status changed unexpectedly.")
    
    # Cleanup (Optional)
    # test_p.delete()

if __name__ == "__main__":
    test_cancel()
