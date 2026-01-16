import asyncio
import edge_tts
import os
from moviepy import AudioFileClip

# Texto de prueba con una emocion clara: Pitch muy alto (+50Hz) para que sea obvio
SSML_TEXT = """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="es-ES">
<voice name="es-ES-AlvaroNeural">
Esta es una prueba de <prosody pitch="+50Hz">voz muy aguda</prosody> y <prosody pitch="-20Hz">voz muy grave</prosody>.
</voice></speak>"""

async def test_ssml_only():
    print("\n--- Test 1: SSML Puro (Sin parametro voice en el constructor) ---")
    communicate = edge_tts.Communicate(SSML_TEXT)
    output = "test_ssml_pure.mp3"
    await communicate.save(output)
    
    clip = AudioFileClip(output)
    print(f"Duracion: {clip.duration:.2f}s")
    clip.close()
    return output

async def test_ssml_with_voice_param():
    print("\n--- Test 2: SSML + Parametro voice (Posible causa de leaks) ---")
    communicate = edge_tts.Communicate(SSML_TEXT, "es-ES-AlvaroNeural")
    output = "test_ssml_with_voice.mp3"
    await communicate.save(output)
    
    clip = AudioFileClip(output)
    print(f"Duracion: {clip.duration:.2f}s")
    clip.close()
    return output

async def main():
    try:
        await test_ssml_only()
        await test_ssml_with_voice_param()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
