import asyncio
import edge_tts
import os
from moviepy import AudioFileClip

async def test_minimal_ssml(pitch_val, name):
    # Minimalist structure known to work with some versions of edge-tts
    ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="es-ES"><voice name="es-ES-AlvaroNeural"><prosody pitch="{pitch_val}">Prueba de pitch {pitch_val}.</prosody></voice></speak>"""
    print(f"\n--- Testing Pitch: {pitch_val} ---")
    output = f"test_pitch_{name}.mp3"
    communicate = edge_tts.Communicate(ssml)
    await communicate.save(output)
    
    clip = AudioFileClip(output)
    print(f"Duracion: {clip.duration:.2f}s")
    clip.close()

async def main():
    # Try percentages instead of Hz
    await test_minimal_ssml("+50%", "pct_plus")
    await test_minimal_ssml("-50%", "pct_minus")
    # Try relative values
    await test_minimal_ssml("high", "high_label")

if __name__ == "__main__":
    asyncio.run(main())
