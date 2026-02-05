import os
import django
import sys

# Add the project directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import Music
from django.conf import settings

def sync_music():
    music_dir = os.path.join(settings.MEDIA_ROOT, 'music')
    if not os.path.exists(music_dir):
        print(f"Error: Directory {music_dir} does not exist.")
        return

    files = [f for f in os.listdir(music_dir) if f.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a'))]
    print(f"Found {len(files)} music files in {music_dir}")

    count_created = 0
    count_updated = 0

    for filename in files:
        relative_path = os.path.join('music', filename)
        name = filename # Use filename as name
        
        # Check if already exists by file path
        music, created = Music.objects.get_or_create(
            file=relative_path,
            defaults={'name': name}
        )
        
        if created:
            count_created += 1
            print(f"Created: {name}")
        else:
            count_updated += 1
            # Ensure name matches filename if it was different
            if music.name != name:
                music.name = name
                music.save()

    print(f"Sync complete. Created {count_created}, Updated {count_updated}.")

if __name__ == "__main__":
    sync_music()
