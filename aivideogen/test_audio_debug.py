import asyncio
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.avgl_engine import generate_audio_edge
from moviepy import AudioFileClip

async def test_audio():
    output = "test_audio_debug.mp3"
    text = "Esto es una prueba de audio para verificar la duracion en el motor v4."
    voice = "es-ES-AlvaroNeural"
    
    print(f"Generating audio to {output}...")
    success = await generate_audio_edge(text, output, voice=voice)
    
    if success and os.path.exists(output):
        clip = AudioFileClip(output)
        print(f"Success! Duration: {clip.duration}")
        clip.close()
    else:
        print("Failed to generate audio.")

if __name__ == "__main__":
    asyncio.run(test_audio())
