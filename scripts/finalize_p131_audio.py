
import os
import django
import sys
import json

# Setup django
sys.path.append(r'c:\Users\hp\aivideogen\aivideogen')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import VideoProject, Music

def finalize_p131():
    p = VideoProject.objects.get(id=131)
    
    # 1. Force Background Music FK
    m = Music.objects.filter(file__icontains='Frame-Dragging').first()
    if m:
        p.background_music = m
        print(f"Musica Global ASIGNADA: {m.name}")
    else:
        print("ERROR: No se encontro la musica Frame-Dragging en la DB.")
        return

    # 2. Update Optimized Audio Parameters
    p.audio_ducking_ratio = 0.55
    p.audio_merge_threshold = 0.4
    p.music_volume = 0.2
    
    # 3. Flatten and Sync script_text (Priority for Video Engine)
    data = json.loads(p.script_text)
    
    # Ensure root-level params exist
    data['background_music'] = m.file.name # Use the actual file path string
    data['audio_ducking_ratio'] = 0.55
    data['audio_merge_threshold'] = 0.4
    data['music_volume'] = 0.2
    data['bg_music_volume'] = 0.2
    
    # Clean internal settings to avoid confusion
    if 'settings' in data:
        data['settings']['audio_ducking_ratio'] = 0.55
        data['settings']['audio_merge_threshold'] = 0.4
    
    p.script_text = json.dumps(data, indent=4, ensure_ascii=False)
    p.save()
    print("Proyecto 131 FINALIZADO y SINCRONIZADO.")

if __name__ == "__main__":
    finalize_p131()
