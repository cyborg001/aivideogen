import os
import django
import sys

# Setup Django
sys.path.append(r'c:\Users\hp\aivideogen\aivideogen')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import VideoProject

def audit_youtube():
    projects = VideoProject.objects.all().order_by('-created_at')[:15]
    print(f"{'ID':<5} | {'Title':<40} | {'Status':<10} | {'YT ID':<20}")
    print("-" * 85)
    for p in projects:
        yt_id = p.youtube_video_id or "N/A"
        print(f"{p.id:<5} | {p.title[:40]:<40} | {p.status:<10} | {yt_id:<20}")
        print(f"Hashtags: {p.script_hashtags}")
        print("-" * 85)

if __name__ == "__main__":
    audit_youtube()
