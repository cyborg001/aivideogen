import asyncio
import edge_tts
import os

async def test_ssml():
    voice = "es-MX-JorgeNeural"
    # Simple SSML
    ssml = f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="es-MX"><voice name="{voice}"><prosody rate="+20%">Hola, esto es una prueba de emoción épica.</prosody></voice></speak>'
    
    print(f"Testing SSML:\n{ssml}")
    
    communicate = edge_tts.Communicate(ssml)
    output_path = "test_ssml_output.mp3"
    
    try:
        await communicate.save(output_path)
        print(f"Success! Audio saved to {output_path}")
        if os.path.exists(output_path):
            print(f"File size: {os.path.getsize(output_path)} bytes")
            # If size is too small, it might have failed silently or just spoke the tags
    except Exception as e:
        print(f"Error during SSML processing: {e}")

if __name__ == "__main__":
    asyncio.run(test_ssml())
