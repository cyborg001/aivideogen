import os
import sys
import django
import threading
import time

# Add base directory to path
BASE_DIR = r'c:\Users\hp\aivideogen\aivideogen'
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import VideoProject
from generator.video_engine import generate_video_avgl

def simulate_cancellation(project_id):
    time.sleep(15) 
    print(f"--- SIMULATING CANCEL for Project {project_id} ---")
    project = VideoProject.objects.get(id=project_id)
    # Corrected status from 'cancel' to 'cancelled'
    project.status = 'cancelled'
    project.save(update_fields=['status'])
    print("--- Status set to 'cancelled' in DB ---")

def test_fixes():
    # Get the last Genghis project as a template
    original = VideoProject.objects.filter(title__icontains='Genghis Khan - Acto 2').last()
    if not original:
        print("No Genghis project found to test.")
        return

    # Create a clone for testing
    import json
    test_p = VideoProject.objects.create(
        title="TEST FINAL FIXES",
        script_text=original.script_text,
        engine='edge',
        aspect_ratio='landscape',
        render_mode='cpu'
    )
    
    print(f"Created Test Project ID: {test_p.id}")

    # Start cancellation thread (optional: comment out to test full run/jitter_id)
    cancel_thread = threading.Thread(target=simulate_cancellation, args=(test_p.id,))
    cancel_thread.start()

    print("Starting render...")
    try:
        generate_video_avgl(test_p)
        print("Render function call returned.")
    except Exception as e:
        print(f"FATAL: Render crashed! Error: {e}")
        import traceback
        traceback.print_exc()

    test_p.refresh_from_db()
    print(f"Final Project Status: {test_p.status}")

if __name__ == "__main__":
    test_fixes()
