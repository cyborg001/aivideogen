import asyncio
import edge_tts

async def main():
    text = "Hola"
    voice = "es-ES-AlvaroNeural"
    comm = edge_tts.Communicate(text, voice)
    for attr in dir(comm):
        try:
            val = getattr(comm, attr)
            if isinstance(val, str) and "<speak" in val:
                print(f"FOUND ATTR: {attr}")
                print(f"VAL: {val}")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main())
