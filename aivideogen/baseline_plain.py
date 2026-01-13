import asyncio
import edge_tts
from moviepy import AudioFileClip

async def main():
    text = "Esta es una prueba de emocion epica."
    voice = "es-ES-AlvaroNeural"
    await edge_tts.Communicate(text, voice).save("baseline_plain.mp3")
    clip = AudioFileClip("baseline_plain.mp3")
    print(f"Plain text duration: {clip.duration:.2f}s")
    clip.close()

if __name__ == "__main__":
    asyncio.run(main())
