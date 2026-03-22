
import os
import django
import sys
import re
from django.db.models import Q

# Setup django
sys.path.append(r'c:\Users\hp\aivideogen\aivideogen')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import VideoProject, Music

def test_lookup():
    project = VideoProject.objects.get(id=131)
    
    global_music_name = None
    if project.background_music:
        try: global_music_name = os.path.basename(project.background_music.file.name)
        except: pass
    
    print(f"Buscando nombre: {global_music_name}")
    
    if global_music_name:
        search_name = os.path.basename(global_music_name).lower()
        name_no_ext = re.sub(r'\.(mp3|wav|m4a)$', '', search_name)
        name_clean = name_no_ext.replace('_', ' ').replace('-', ' ').strip()
        name_slug = name_no_ext.replace(' ', '_').replace('-', '_').strip()
        
        print(f"  Variaciones: {name_no_ext} | {name_clean} | {name_slug}")
        
        gm_obj = Music.objects.filter(
            Q(file__icontains=name_no_ext) | 
            Q(file__icontains=name_slug) | 
            Q(name__icontains=name_clean) |
            Q(name__icontains=name_no_ext)
        ).first()
        
        if gm_obj:
            print(f"  OK: Encontrado: {gm_obj.name} -> {gm_obj.file.path}")
            print(f"  Archivo existe: {os.path.exists(gm_obj.file.path)}")
        else:
            print(f"  ERROR: No encontrado en DB")

if __name__ == "__main__":
    test_lookup()
