import asyncio
import edge_tts
from moviepy import AudioFileClip

async def main():
    voice = "es-ES-AlvaroNeural"
    # Content with tags UNESCAPED
    inner_text = "Esta es una prueba de <prosody pitch='+10%'>emocion epica</prosody>."
    
    comm = edge_tts.Communicate(inner_text, voice)
    
    # Debug: what did it do?
    # edge-tts 7.x stores parts in self.texts
    print(f"Before Patch: {comm.texts}")
    
    # PATCH IT
    comm.texts = [t.replace("&lt;prosody", "<prosody").replace("&gt;", ">").replace("&lt;/prosody", "</prosody") for t in comm.texts]
    print(f"After Patch: {comm.texts}")
    
    await comm.save("test_patched_v2.mp3")
    
    clip = AudioFileClip("test_patched_v2.mp3")
    print(f"Duration: {clip.duration:.2f}s")
    clip.close()

if __name__ == "__main__":
    asyncio.run(main())
