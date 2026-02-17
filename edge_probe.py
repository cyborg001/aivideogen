import asyncio
import edge_tts

async def probe():
    text = "Hola Arquitecto, esto es una prueba de sincronizacion de palabras."
    voice = "es-ES-AlvaroNeural"
    communicate = edge_tts.Communicate(text, voice)
    
    print(f"Probando stream para: '{text}'")
    events_found = []
    async for event in communicate.stream():
        if event["type"] != "audio":
            print(f"EVENTO: {event}")
            events_found.append(event["type"])
    
    if "WordBoundary" in events_found or "word_boundary" in events_found or "wordboundary" in [e.lower() for e in events_found]:
        print("\n✅ EXITOSO: Se encontraron eventos de WordBoundary.")
    else:
        print("\n❌ FALLO: No se encontraron eventos de WordBoundary.")
        print(f"Tipos encontrados: {set(events_found)}")

if __name__ == "__main__":
    asyncio.run(probe())
