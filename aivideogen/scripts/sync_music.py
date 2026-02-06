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
        name = filename # Use filename as name
        
        # Robust check Layer 1: Does this exact path exist in DB?
        # Robust check Layer 2: Is there any entry where the filename is the same?
        # Robust check Layer 3: Is there any entry where name (stored label) is the same?
        
        existing = Music.objects.filter(file__icontains=filename).first() or \
                   Music.objects.filter(name__iexact=name).first()
        
        if not existing:
            relative_path = os.path.join('music', filename)
            Music.objects.create(
                file=relative_path,
                name=name
            )
            count_created += 1
            print(f"Created: {name}")
        else:
            count_updated += 1
            # Ensure name matches filename if it was different
            if existing.name != name:
                existing.name = name
                existing.save()

    print(f"Sync complete. Created {count_created}, Updated {count_updated}.")

if __name__ == "__main__":
    sync_music()
