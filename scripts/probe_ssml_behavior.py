import asyncio
import edge_tts
import os

async def test_ssml():
    # Test 1: Full SSML with namespace and voice
    ssml_full = """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="es-MX"><voice name="es-MX-DaliaNeural">Hola, esto es una prueba de SSML completo.</voice></speak>"""
    
    # Test 2: Minimal SSML
    ssml_min = """<speak version="1.0" xml:lang="es-MX">Hola, esto es una prueba de SSML mínimo.</speak>"""
    
    # Test 3: Standard string (for comparison)
    text_plain = "Hola, esto es una prueba de texto plano."

    print("--- Probando SSML Full ---")
    try:
        communicate = edge_tts.Communicate(ssml_full)
        await communicate.save("test_full.mp3")
        print("Test Full generado.")
    except Exception as e:
        print(f"Error en Test Full: {e}")

    print("\n--- Probando SSML Min ---")
    try:
        communicate = edge_tts.Communicate(ssml_min, "es-MX-DaliaNeural")
        await communicate.save("test_min.mp3")
        print("Test Min generado.")
    except Exception as e:
        print(f"Error en Test Min: {e}")

if __name__ == "__main__":
    asyncio.run(test_ssml())
