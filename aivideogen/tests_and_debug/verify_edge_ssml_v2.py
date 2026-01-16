import asyncio
import edge_tts
import os
from moviepy import AudioFileClip

async def run_test(ssml, name):
    print(f"\n--- Testing: {name} ---")
    print(f"Content: {ssml}")
    output = f"test_{name}.mp3"
    communicate = edge_tts.Communicate(ssml)
    await communicate.save(output)
    
    clip = AudioFileClip(output)
    print(f"Duracion: {clip.duration:.2f}s")
    clip.close()

async def main():
    # TEST 3: Simple speak without voice tag (assuming voice is handled by Communicate if we pass it, OR we don't pass it)
    # Actually Communicate REQUIRES a voice if not in SSML. 
    # Let's try the MOST standard header possible.
    
    # A: Just <speak> and voice parameter
    await run_test("<speak>Prueba simple de SSML.</speak>", "simple_speak")
    
    # B: SSML with voice tag but NO namespace
    ssml_no_ns = """<speak><voice name="es-ES-AlvaroNeural">Prueba sin namespaces.</voice></speak>"""
    await run_test(ssml_no_ns, "no_ns")

    # C: SSML with character escaping (CRITICAL)
    ssml_escaped = """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="es-ES"><voice name="es-ES-AlvaroNeural">Prueba de <prosody pitch="+20Hz">tono alto</prosody>.</voice></speak>"""
    await run_test(ssml_escaped, "escaped_standard")

if __name__ == "__main__":
    asyncio.run(main())
