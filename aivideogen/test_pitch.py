import asyncio
import edge_tts
from moviepy import AudioFileClip

async def main():
    voice = "es-ES-AlvaroNeural"
    # Header from internal wrap
    header = f"<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'><voice name='{voice}'>"
    footer = "</voice></speak>"
    
    # CASE 1: With Hz
    ssml_hz = f"{header}Prueba con hercios <prosody pitch='+5Hz'>epico</prosody>{footer}"
    
    # CASE 2: With Percentage
    ssml_pct = f"{header}Prueba con porcentaje <prosody pitch='+10%'>epico</prosody>{footer}"
    
    await edge_tts.Communicate(ssml_hz).save("test_hz.mp3")
    await edge_tts.Communicate(ssml_pct).save("test_pct.mp3")
    
    print(f"Duration Hz: {AudioFileClip('test_hz.mp3').duration:.2f}s")
    print(f"Duration Pct: {AudioFileClip('test_pct.mp3').duration:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())
