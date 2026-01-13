import asyncio
import edge_tts

async def main():
    text = "Probando"
    voice = "es-ES-AlvaroNeural"
    comm = edge_tts.Communicate(text, voice)
    # Search all attributes for "Probando"
    for attr in dir(comm):
        try:
            val = getattr(comm, attr)
            if isinstance(val, str) and "Probando" in val:
                print(f"Attr: {attr}, Val: {val}")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main())
