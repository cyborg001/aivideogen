import asyncio
import edge_tts
import time

TEXT_CONTENT = "Esta es una prueba de <prosody pitch='+10Hz'>emocion epica</prosody>."
VOICE = "es-ES-AlvaroNeural"

async def test(header, footer, name):
    ssml = f"{header}{TEXT_CONTENT}{footer}"
    print(f"\n--- Testing {name} ---")
    print(f"SSML: {ssml}")
    
    # TEST A: With voice in constructor
    communicate_a = edge_tts.Communicate(ssml, VOICE)
    await communicate_a.save(f"test_A_{name}.mp3")
    
    # TEST B: Without voice in constructor (SSML only)
    communicate_b = edge_tts.Communicate(ssml)
    await communicate_b.save(f"test_B_{name}.mp3")
    
    from moviepy import AudioFileClip
    clip_a = AudioFileClip(f"test_A_{name}.mp3")
    clip_b = AudioFileClip(f"test_B_{name}.mp3")
    print(f"Audio Duration A (with voice param): {clip_a.duration:.2f}s")
    print(f"Audio Duration B (NO voice param): {clip_b.duration:.2f}s")
    clip_a.close()
    clip_b.close()

async def main():
    # H1: Minimal
    await test("<speak>", "</speak>", "H1_minimal")
    
    # H2: Full (Standard)
    await test('<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="es-ES">', "</speak>", "H2_full")

if __name__ == "__main__":
    asyncio.run(main())
