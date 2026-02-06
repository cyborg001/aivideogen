import os
import django
import sys
import re

# Add the project directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import Music
from django.conf import settings

def cleanup_music():
    music_dir = os.path.join(settings.MEDIA_ROOT, 'music')
    if not os.path.exists(music_dir):
        print(f"Error: Directory {music_dir} does not exist.")
        return

    files = os.listdir(music_dir)
    print(f"Analyzing {len(files)} files in {music_dir}...")

    # Pattern for Django suffixes: _[a-zA-Z0-9]{7}.mp3
    suffix_pattern = re.compile(r'(.+?)_[a-zA-Z0-9]{7}(\.[a-zA-Z0-9]+)$')
    
    count_deleted = 0
    
    for filename in files:
        match = suffix_pattern.match(filename)
        if match:
            base_name = match.group(1)
            ext = match.group(2)
            original = base_name + ext
            
            # If the original file exists, this is likely a duplicate
            if original in files:
                file_path = os.path.join(music_dir, filename)
                print(f"Found duplicate: {filename} -> Original: {original}")
                
                # Delete from Database
                Music.objects.filter(file__icontains=filename).delete()
                
                # Delete from Disk
                try:
                    os.remove(file_path)
                    count_deleted += 1
                except Exception as e:
                    print(f"Error deleting {filename}: {e}")
                    
    print(f"Cleanup complete. Deleted {count_deleted} duplicate files.")

if __name__ == "__main__":
    cleanup_music()
