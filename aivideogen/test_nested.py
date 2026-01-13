import asyncio
import edge_tts
from moviepy import AudioFileClip

async def main():
    voice = "es-ES-AlvaroNeural"
    # We provide a <voice> tag but NO <speak> tag.
    # edge-tts will wrap it in <speak> and escape the <voice>... wait.
    # If it doesn't start with <speak, it escapes everything!
    # So <voice> will become &lt;voice&gt;.
    
    inner_text = f"<voice name='{voice}'>Prueba de <prosody pitch='+10%'>emocion</prosody></voice>"
    
    await edge_tts.Communicate(inner_text, voice).save("test_nested.mp3")
    clip = AudioFileClip("test_nested.mp3")
    print(f"Duration: {clip.duration:.2f}s")
    clip.close()

if __name__ == "__main__":
    asyncio.run(main())
