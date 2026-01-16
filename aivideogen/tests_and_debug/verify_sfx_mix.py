import os
import sys
from moviepy import AudioFileClip, CompositeAudioClip, afx

# Configurar rutas
BASE_DIR = r"c:\Users\Usuario\Documents\curso creacion contenido con ia\aivideogen3\aivideogen"
VOICE_PATH = os.path.join(BASE_DIR, "debug_audio_minimal.mp3")
SFX_PATH = os.path.join(BASE_DIR, "media", "sfx", "Power_Tool_Electrical_Buzz.mp3")
OUTPUT_PATH = os.path.join(BASE_DIR, "test_sfx_mix_result.mp3")

def test_mix():
    print(f"--- Iniciando prueba de mezcla SFX ---")
    
    if not os.path.exists(VOICE_PATH):
        print(f"Error: No se encuentra la voz en {VOICE_PATH}")
        return
    if not os.path.exists(SFX_PATH):
        print(f"Error: No se encuentra el SFX en {SFX_PATH}")
        return

    try:
        # Cargar clips
        voice = AudioFileClip(VOICE_PATH)
        sfx = AudioFileClip(SFX_PATH).with_effects([afx.MultiplyVolume(0.5)])
        
        print(f"Voz duracion: {voice.duration}s")
        print(f"SFX duracion original: {sfx.duration}s")
        
        # Limitar SFX a la duración de la voz (como hace el motor)
        sfx_trimmed = sfx.with_duration(min(sfx.duration, voice.duration))
        
        # Mezclar (Iniciando ambos en 0)
        mixed = CompositeAudioClip([voice, sfx_trimmed.with_start(0)])
        
        print(f"Mezclando y exportando a {OUTPUT_PATH}...")
        mixed.write_audiofile(OUTPUT_PATH, fps=44100)
        print("✅ ¡Éxito! El archivo de mezcla ha sido generado.")
        
    except Exception as e:
        print(f"❌ Error durante la mezcla: {e}")

if __name__ == "__main__":
    test_mix()
