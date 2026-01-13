import asyncio
import edge_tts

async def main():
    text = "Esta es una prueba de emocion epica."
    voice = "es-ES-AlvaroNeural"
    comm = edge_tts.Communicate(text, voice)
    # The internal text is constructed after Communicate is called?
    # No, it's in the constructor.
    # WAIT! It's actually constructed in _generate_payload or similar?
    # No, in common.py it's in constructor.
    print(f"Internal String: {comm.text}")

if __name__ == "__main__":
    asyncio.run(main())
