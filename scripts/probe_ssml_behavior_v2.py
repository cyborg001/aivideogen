import asyncio
import edge_tts
import os

async def test_ssml_v2():
    voice = "es-DO-EmilioNeural"
    lang = "es-DO"
    content = '<prosody rate="+10%">Prueba de velocidad con prosodia.</prosody>'
    
    # Test 4: No internal <voice> tag, but passing voice to Communicate
    ssml_v4 = f'<speak version="1.0" xml:lang="{lang}">{content}</speak>'
    
    # Test 5: Standard SSML but with no xmlns URL
    # (Sometimes the URL triggers literal reading if the parser is simple)
    ssml_v5 = f'<speak version="1.0" xml:lang="{lang}"><voice name="{voice}">{content}</voice></speak>'

    print("--- Probando SSML V4 (No internal voice tag) ---")
    try:
        communicate = edge_tts.Communicate(ssml_v4, voice)
        await communicate.save("test_v4.mp3")
        print("Test V4 generado.")
    except Exception as e:
        print(f"Error en Test V4: {e}")

    print("\n--- Probando SSML V5 (Standard with voice, NO xmlns) ---")
    try:
        communicate = edge_tts.Communicate(ssml_v5)
        await communicate.save("test_v5.mp3")
        print("Test V5 generado.")
    except Exception as e:
        print(f"Error en Test V5: {e}")

if __name__ == "__main__":
    asyncio.run(test_ssml_v2())
