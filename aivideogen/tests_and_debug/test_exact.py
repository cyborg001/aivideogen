import asyncio
import edge_tts
from moviepy import AudioFileClip

# Exact string produced internally by Communicate("Esta es una prueba de emocion epica.", "es-ES-AlvaroNeural")
SSML_A = "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'><voice name='es-ES-AlvaroNeural'>Esta es una prueba de emocion epica.</voice></speak>"

async def main():
    print(f"Testing Exact Internal String...")
    
    # Case 1: Pass as text (starts with <speak)
    await edge_tts.Communicate(SSML_A).save("exact_A.mp3")
    
    # Case 2: Pass as text BUT let it wrap (it won't wrap because it starts with <speak)
    await edge_tts.Communicate(SSML_A, "es-ES-AlvaroNeural").save("exact_B.mp3")

    duration_a = AudioFileClip("exact_A.mp3").duration
    duration_b = AudioFileClip("exact_B.mp3").duration
    
    print(f"Duration A (No voice param): {duration_a:.2f}s")
    print(f"Duration B (With voice param): {duration_b:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())
