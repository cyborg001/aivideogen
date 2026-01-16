import asyncio
import edge_tts
import os
from moviepy import AudioFileClip

# SSML completo con voz incluida
SSML_COMPLETO = """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="es-ES">
<voice name="es-ES-AlvaroNeural">
Esta es una prueba de <prosody pitch="+50Hz">voz extremadamente aguda</prosody>.
</voice></speak>"""

async def test_fixed_approach():
    print("\n--- Test Final: SSML sin parametros extra ---")
    # CRUCIAL: No pasar VOICE ni RATE aqui si ya estan en el SSML
    communicate = edge_tts.Communicate(SSML_COMPLETO)
    output = "test_fixed_ssml.mp3"
    await communicate.save(output)
    
    clip = AudioFileClip(output)
    print(f"Duracion: {clip.duration:.2f}s")
    if clip.duration < 10:
        print("✅ ¡EXITO! La duracion es normal. El SSML ha sido aceptado.")
    else:
        print("❌ FALLO: Sigue habiendo blooming/bloating.")
    clip.close()

if __name__ == "__main__":
    asyncio.run(test_fixed_approach())
