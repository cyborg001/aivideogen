import asyncio
import edge_tts
import time

# compact SSML
SSML = "<speak>Esta es una prueba de <prosody pitch='+10Hz'>emocion epica</prosody>.</speak>"
VOICE = "es-ES-AlvaroNeural"

async def main():
    print(f"Testing compact SSML...")
    communicate = edge_tts.Communicate(SSML, VOICE)
    await communicate.save("test_compact.mp3")
    
    from moviepy import AudioFileClip
    clip = AudioFileClip("test_compact.mp3")
    print(f"Duration: {clip.duration:.2f}s")
    clip.close()

if __name__ == "__main__":
    asyncio.run(main())
