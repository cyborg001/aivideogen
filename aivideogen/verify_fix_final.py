import asyncio
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.avgl_engine import translate_emotions, wrap_ssml
import edge_tts

async def test_audio(text, voice, filename, use_ssml):
    print(f"\n--- Testing: {filename} (use_ssml={use_ssml}) ---")
    translated = translate_emotions(text, use_ssml=use_ssml)
    ssml = wrap_ssml(translated, voice)
    print(f"Final Text/SSML: {ssml}")
    
    # We simulate the call in generate_audio_edge
    from generator.avgl_engine import generate_audio_edge
    success = await generate_audio_edge(ssml, filename, voice)
    
    if success:
        from moviepy import AudioFileClip
        clip = AudioFileClip(filename)
        print(f"Duration: {clip.duration:.2f}s")
        clip.close()
    else:
        print("FAIL")

async def main():
    voice = "es-ES-AlvaroNeural"
    
    # Test 1: Clean mode (Edge TTS)
    await test_audio("[EPICO] Las estrellas son los ojos de la creación. [/EPICO]", voice, "verify_clean.mp3", use_ssml=False)
    
    # Test 2: Pause in clean mode
    await test_audio("Inicia [PAUSA:1.0] Fin", voice, "verify_pause_clean.mp3", use_ssml=False)

if __name__ == "__main__":
    asyncio.run(main())
