import asyncio
import edge_tts
import os
import time

# Minimal Header (Current in avgl_engine.py)
MINIMAL_SSML = """<speak>Esta es una prueba de <prosody pitch="+5Hz">emocion epica</prosody>.</speak>"""

# Full Header (Recommended in many docs)
FULL_SSML = """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="es-ES"><prosody pitch="+5Hz">Esta es una prueba de emocion epica.</prosody></speak>"""

# Plain Text with tag leaking (Mocking if SSML fails)
PLAIN_TEXT = """Esta es una prueba de <prosody pitch="+5Hz">emocion epica</prosody>."""

VOICE = "es-ES-AlvaroNeural"

async def generate_and_check(text, filename):
    print(f"\n--- Testing: {filename} ---")
    print(f"SSML: {text}")
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(filename)
    
    from moviepy import AudioFileClip
    clip = AudioFileClip(filename)
    print(f"Duration: {clip.duration:.2f}s")
    clip.close()

async def main():
    try:
        await generate_and_check(MINIMAL_SSML, "test_minimal.mp3")
        await generate_and_check(FULL_SSML, "test_full.mp3")
        await generate_and_check(PLAIN_TEXT, "test_plain.mp3")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
