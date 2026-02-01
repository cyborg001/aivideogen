
import os
import django
import sys

sys.path.append(r"c:\Users\Usuario\Documents\curso creacion contenido con ia\aivideogen3")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aivideogen.settings')
django.setup()

from generator.models import VideoProject

def check_status():
    processing = VideoProject.objects.filter(status='processing').first()
    if processing:
        print(f"Project Generating: {processing.title} (ID: {processing.id})")
        print(f"Auto Upload Enabled: {processing.auto_upload_youtube}")
    else:
        print("No project is currently processing.")
        # Check for recently completed
        completed = VideoProject.objects.filter(status='completed').order_by('-created_at').first()
        if completed:
            print(f"Last Completed: {completed.title} (ID: {completed.id}) - Uploaded: {completed.youtube_url}")

if __name__ == "__main__":
    check_status()
