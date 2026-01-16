import asyncio
import edge_tts
import time

TEXT_CONTENT = "Esta es una prueba de <prosody pitch='+10Hz'>emocion epica</prosody>."
VOICE = "es-ES-AlvaroNeural"

async def test(header, footer, name):
    ssml = f"{header}{TEXT_CONTENT}{footer}"
    print(f"\n--- Testing {name} ---")
    print(f"SSML: {ssml}")
    start = time.time()
    communicate = edge_tts.Communicate(ssml, VOICE)
    await communicate.save(f"experiment_{name}.mp3")
    elapsed = time.time() - start
    
    from moviepy import AudioFileClip
    clip = AudioFileClip(f"experiment_{name}.mp3")
    print(f"Time to generate: {elapsed:.2f}s")
    print(f"Audio Duration: {clip.duration:.2f}s")
    clip.close()

async def main():
    # H1: Minimal (Broken according to user)
    await test("<speak>", "</speak>", "H1_minimal")
    
    # H2: Full (30s Bloat detected in Step 104)
    await test('<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="es-ES"><voice name="es-ES-AlvaroNeural">', "</voice></speak>", "H2_full")
    
    # H3: No xmlns, only xml:lang
    await test('<speak version="1.0" xml:lang="es-ES">', "</speak>", "H3_no_xmlns")
    
    # H4: Just voice tag inside speak
    await test('<speak><voice name="es-ES-AlvaroNeural">', "</voice></speak>", "H4_voice_only")
    
    # H5: Standard Header, NO voice tag inside
    await test('<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="es-ES">', "</speak>", "H5_standard_no_voice")

    # H6: Minimal with xml:lang only
    await test('<speak xml:lang="es-ES">', "</speak>", "H6_minimal_lang")

if __name__ == "__main__":
    asyncio.run(main())
