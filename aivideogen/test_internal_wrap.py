import asyncio
import edge_tts
import time

# Inner content with tags
INNER_CONTENT = "Esta es una prueba de <prosody pitch='+10Hz'>emocion epica</prosody>."
VOICE = "es-ES-AlvaroNeural"

async def main():
    print(f"Testing inner content only (letting edge-tts wrap)...")
    # This is what happen if we DON'T use wrap_ssml but use edge_tts.Communicate(text, voice)
    communicate = edge_tts.Communicate(INNER_CONTENT, VOICE)
    await communicate.save("test_internal_wrap.mp3")
    
    from moviepy import AudioFileClip
    clip = AudioFileClip("test_internal_wrap.mp3")
    print(f"Duration: {clip.duration:.2f}s")
    clip.close()

if __name__ == "__main__":
    asyncio.run(main())
