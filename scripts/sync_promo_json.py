
import os
import django
import sys
import json

# Setup django
sys.path.append(r'c:\Users\hp\aivideogen\aivideogen')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import VideoProject, Music

def sync():
    # 1. Read the JSON file
    json_path = r'c:\Users\hp\aivideogen\aivideogen\guiones\cyborg001\promo_velo_gravitacional.avgl.json'
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 2. Clean and Flatten structure (Ensure top-level priority)
    # If there's an old 'settings' dict, merge it up then delete it
    if 'settings' in data:
        settings_data = data.pop('settings')
        for k, v in settings_data.items():
            if k not in data or data[k] is None:
                data[k] = v

    # 3. Explicitly set optimized audio parameters at TOP LEVEL
    data['audio_ducking_ratio'] = 0.55
    data['audio_merge_threshold'] = 0.4
    data['music_volume'] = 0.2
    data['bg_music_volume'] = 0.2
    data['voice_speed'] = data.get('voice_speed', '+0%')
    
    # Ensure background_music is set
    if not data.get('background_music'):
         data['background_music'] = "Frame-Dragging - The Grey Room _ Density & Time.mp3"

    # 4. Update DB Project 131 (Model Fields + Script Text)
    p = VideoProject.objects.get(id=131)
    p.title = data.get('title', p.title)
    
    # Update Model Fields (Priority for Video Engine)
    p.audio_ducking_ratio = 0.55
    p.audio_merge_threshold = 0.4
    p.music_volume = 0.2
    p.voice_id = data.get('voice', 'es-ES-AlvaroNeural')
    
    # Find background music object for the relationship field
    m_name = data['background_music']
    m_obj = Music.objects.filter(file__icontains="Frame-Dragging").first()
    if m_obj:
        p.background_music = m_obj
        print(f"Buscando música: {m_obj.name} conectada al proyecto.")

    p.script_text = json.dumps(data, indent=4)
    p.save()

    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

    print(f"Proyecto 131 sincronizado y saneado.")
    print(f"   - Ducking: {p.audio_ducking_ratio}")
    print(f"   - Merge Threshold: {p.audio_merge_threshold}")
    print(f"   - Script JSON flat: {len(data.keys())} keys at top level.")

if __name__ == "__main__":
    sync()
