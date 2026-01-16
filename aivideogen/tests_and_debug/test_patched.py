import asyncio
import edge_tts
from xml.sax.saxutils import escape

class SSMLCommunicate(edge_tts.Communicate):
    def __init__(self, text, voice, **kwargs):
        # We manually wrap it in SSML but WITHOUT ESCAPING the tags
        # actually, edge-tts constructor does:
        # self.text = f"<speak...>{escape(text)}</voice></speak>"
        # We can just override the self.text after calling super()
        super().__init__(text, voice, **kwargs)
        
        # Now we replace the escaped tags back to real tags
        # This is a bit hacky but it should work
        self.text = self.text.replace("&lt;prosody", "<prosody").replace("&lt;/prosody&gt;", "</prosody>")
        self.text = self.text.replace("&lt;break", "<break").replace("/&gt;", "/>")
        # Ensure we didn't break actually escaped characters
        print(f"Patched SSML: {self.text}")

async def main():
    text = "Esta es una prueba de <prosody pitch='+10%'>emocion epica</prosody>."
    voice = "es-ES-AlvaroNeural"
    comm = SSMLCommunicate(text, voice)
    await comm.save("test_patched.mp3")
    
    from moviepy import AudioFileClip
    clip = AudioFileClip("test_patched.mp3")
    print(f"Duration: {clip.duration:.2f}s")
    clip.close()

if __name__ == "__main__":
    asyncio.run(main())
