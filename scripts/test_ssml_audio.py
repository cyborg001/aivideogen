import os
import django
import asyncio
import sys

# Setup Django
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'aivideogen'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from aivideogen.generator.avgl_engine import parse_avgl_json, convert_text_to_avgl_json, generate_audio_edge
from django.conf import settings

async def test_ssml():
    guion_path = r"c:\Users\hp\aivideogen\aivideogen\guiones\test_emociones_ssml.md"
    with open(guion_path, "r", encoding="utf-8") as f:
        text = f.read()
    
    # 1. Convert to JSON then Parse to Script object
    data = convert_text_to_avgl_json(text, title="Test SSML")
    from aivideogen.generator.avgl_engine import parse_avgl_json
    import json
    script = parse_avgl_json(json.dumps(data))
    
    print(f"--- Iniciando prueba de Audio para: {script.title} ---")
    
    scene = script.get_all_scenes()[0]
    output_audio = os.path.join(settings.MEDIA_ROOT, "test_ssml_audio.mp3")
    
    print(f"Texto original: {scene.text}")
    
    # generate_audio_edge handles the SSML wrapping internally now in v17.2.14
    success = await generate_audio_edge(
        scene.text, 
        output_audio, 
        voice="es-MX-JorgeNeural",
        scene=scene
    )
    
    if success:
        print(f"✅ ÉXITO: Audio generado en {output_audio}")
        if scene.word_timings:
            print(f"✅ Word Timings capturados: {len(scene.word_timings)} palabras.")
        else:
            print("⚠️ ADVERTENCIA: No se capturaron Word Timings.")
    else:
        print("❌ ERROR: La generación de audio falló. Probablemente el SSML no es válido para Edge TTS.")

if __name__ == "__main__":
    asyncio.run(test_ssml())
