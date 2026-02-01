import asyncio
import os
import sys
import django

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.avgl_engine import generate_audio_edge, AVGLScene

async def test_intervals():
    scene = AVGLScene("Test Scene")
    text = "Hola. [PAUSA:2.5] Probando el ducking granular."
    output_path = "media/temp_audio/test_ducking_granular.mp3"
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"--- Generando audio para: {text} ---")
    success = await generate_audio_edge(text, output_path, scene=scene)
    
    if success:
        print(f"[OK] Audio generado en: {output_path}")
        print(f"[DATA] Intervalos de voz detectados: {scene.voice_intervals}")
        
        # Validation
        if len(scene.voice_intervals) == 2:
            start1, end1 = scene.voice_intervals[0]
            start2, end2 = scene.voice_intervals[1]
            gap = start2 - end1
            print(f"[TIME] Espacio entre segmentos: {gap:.2f}s (Esperado: ~2.5s)")
            
            if 2.4 <= gap <= 2.8:
                print("[SUCCESS] VERIFICACION EXITOSA: Granularidad detectada correctamente.")
            else:
                 print("[WARNING] ALERTA: El gap no coincide con lo esperado.")
        else:
            print(f"[ERROR] Se esperaban 2 intervalos, se obtuvieron {len(scene.voice_intervals)}")
    else:
        print("[ERROR] Fallo la generacion de audio.")

if __name__ == "__main__":
    asyncio.run(test_intervals())
