import asyncio
import edge_tts
from moviepy import AudioFileClip

# This is exactly what edge-tts does internally:
def edge_tts_internal_mock(text, voice):
    return (
        f"<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' "
        f"xml:lang='en-US'><voice name='{voice}'>{text}</voice></speak>"
    )

async def main():
    voice = "es-ES-AlvaroNeural"
    # Note: We DON'T escape the inner tags, because we want them to be tags.
    inner_text = "Esta es una prueba de <prosody pitch='+10Hz'>emocion epica</prosody>."
    ssml = edge_tts_internal_mock(inner_text, voice)
    print(f"Testing Mock SSML: {ssml}")
    
    await edge_tts.Communicate(ssml).save("test_mock.mp3")
    clip = AudioFileClip("test_mock.mp3")
    print(f"Duration: {clip.duration:.2f}s")
    clip.close()

if __name__ == "__main__":
    asyncio.run(main())
