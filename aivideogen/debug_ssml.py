import os
import sys
import json
import django
from django.conf import settings

# Setup minimal Django environment
# Add current directory to path so 'aivideogen' module is found
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
# Also add parent dir if needed, but current dir (manage.py location) usually sufficient
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aivideogen.settings')
django.setup()

from generator.avgl_engine import parse_avgl_json, translate_emotions, wrap_ssml

def debug_file(file_path):
    print(f"📂 Leyendo archivo: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    print(f"✅ Archivo leído ({len(content)} bytes). Parseando JSON...")
    
    try:
        script = parse_avgl_json(content)
        print(f"🎬 Título del Video: {script.title}")
        print(f"🗣️  Voz Global: {script.voice}")
        print("-" * 50)
        
        scenes = script.get_all_scenes()
        for i, scene in enumerate(scenes):
            print(f"\n--- ESCENA {i+1}: {scene.title} ---")
            
            # 1. Raw Text extraction
            print(f"📝 Texto Original (JSON):")
            print(f"   '{scene.text}'")
            
            # 2. Emotion Translation
            text_with_emotions = translate_emotions(scene.text)
            if text_with_emotions != scene.text:
                print(f"✨ Texto con Emociones/Pausas:")
                print(f"   '{text_with_emotions}'")
            
            # 3. SSML Wrapping
            # Calculate speed rate like video_engine does
            speed_rate = f"+{int((scene.speed - 1.0) * 100)}%"
            ssml = wrap_ssml(text_with_emotions, scene.voice, speed_rate)
            
            print(f"📤 LO QUE SE MANDA A EDGE-TTS (SSML):")
            if ssml.startswith('<speak'):
                # Pretty print xml if possible, or just raw
                print(f"   {ssml}")
            else:
                print(f"   (Texto plano, sin SSML explícito)")
                print(f"   '{ssml}'")
                print(f"   [Parametro rate='{speed_rate}' se pasará aparte]")

    except Exception as e:
        print(f"❌ ERROR al procesar: {e}")

if __name__ == "__main__":
    target_file = r"c:\Users\Usuario\Documents\curso creacion contenido con ia\aivideogen3\aivideogen\docs\EJEMPLOS\guion_ejemplo_ia_v4.json"
    debug_file(target_file)
