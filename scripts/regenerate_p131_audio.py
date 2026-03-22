
import os
import django
import sys
import json
import asyncio
import time

# Setup django
sys.path.append(r'c:\Users\hp\aivideogen\aivideogen')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"  # Allow DB access from async loop
django.setup()

from generator.models import VideoProject
from generator.avgl_engine import parse_avgl_json, generate_audio_edge

async def generate_scene_audio(scene, audio_path, voice, speed):
    try:
        import re
        curr_text = re.sub(r'\(.*?\)', '', scene.text).strip()
        success = await generate_audio_edge(curr_text, audio_path, voice, speed)
        return success
    except Exception as e:
        print(f"Error en escena: {e}")
        return False

async def main():
    # Fix encoding for Windows console
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        
    print("Iniciando regeneracion de audio para Proyecto 131...")
    
    p = VideoProject.objects.get(id=131)
    script = parse_avgl_json(p.script_text)
    voice_id = p.voice_id or "es-ES-AlvaroNeural"
    
    temp_audio_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'aivideogen', 'media', 'temp_audio')
    os.makedirs(temp_audio_dir, exist_ok=True)
    
    all_scenes = script.get_all_scenes()
    for i, scene in enumerate(all_scenes):
        audio_name = f"project_131_scene_{i:03d}.mp3"
        audio_path = os.path.join(temp_audio_dir, audio_name)
        
        print(f"  Segmento {i+1}/{len(all_scenes)}: {audio_name}")
        
        voice = scene.voice or voice_id
        speed = "+0%" # Default
        
        success = await generate_scene_audio(scene, audio_path, voice, speed)
        if success:
            print(f"    OK")
        else:
            print(f"    ERROR")

    print("Regeneracion completada.")

if __name__ == "__main__":
    asyncio.run(main())
