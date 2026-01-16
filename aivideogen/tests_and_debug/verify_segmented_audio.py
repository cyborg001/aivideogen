import asyncio
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.avgl_engine import generate_audio_edge

async def test():
    text = "[EPICO] Inicia prueba. [/EPICO] [PAUSA:1.5] [SUSURRO] Fin de prueba. [/SUSURRO]"
    output = "final_segmented_test.mp3"
    voice = "es-ES-AlvaroNeural"
    
    print("Testing segmented audio...")
    success = await generate_audio_edge(text, output, voice)
    
    if success:
        print(f"SUCCESS: {output} generated.")
        from moviepy import AudioFileClip
        clip = AudioFileClip(output)
        print(f"Final Duration: {clip.duration:.2f}s")
        clip.close()
    else:
        print("FAIL: Segmentation error.")

if __name__ == "__main__":
    asyncio.run(test())
