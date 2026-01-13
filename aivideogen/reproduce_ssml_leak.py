import asyncio
import edge_tts
import os
import xml.sax.saxutils as saxutils
import re

# Logic from avgl_engine.py
def translate_emotions(text):
    emotions = {
        'TENSO': {'pitch': '-10Hz', 'rate': '-15%'},
        'EPICO': {'pitch': '+5Hz', 'rate': '+10%', 'volume': '+15%'},
        'SUSPENSO': {'pitch': '-5Hz', 'rate': '-25%'},
        'GRITANDO': {'pitch': '+15Hz', 'rate': '+20%', 'volume': 'loud'},
        'SUSURRO': {'pitch': '-12Hz', 'rate': '-20%', 'volume': '-30%'},
    }
    
    processed_text = saxutils.escape(text)
    
    for tag, attrs in emotions.items():
        pattern = rf'\[{tag}\](.*?)\[/{tag}\]'
        attr_str = " ".join([f'{k}="{v}"' for k, v in attrs.items()])
        replacement = rf'<prosody {attr_str}>\1</prosody>'
        processed_text = re.sub(pattern, replacement, processed_text, flags=re.IGNORECASE | re.DOTALL)
    
    processed_text = re.sub(r'\[PAUSA:([\d\.]+)\]', r'<break time="\1s"/>', processed_text, flags=re.IGNORECASE)
    return processed_text

def wrap_ssml_minimal(text, speed="+0%"):
    if '<prosody' in text or '<break' in text:
        content = text
        if speed != "+0%":
            content = f'<prosody rate="{speed}">{text}</prosody>'
        return f'<speak>{content}</speak>'
    return text

def wrap_ssml_full(text, voice, speed="+0%"):
    if '<prosody' in text or '<break' in text:
        content = text
        if speed != "+0%":
            content = f'<prosody rate="{speed}">{text}</prosody>'
        return f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="es-ES"><voice name="{voice}">{content}</voice></speak>'
    return text

async def test_audio(text, filename, voice="es-ES-AlvaroNeural"):
    print(f"Generating {filename}...")
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)
    print(f"Done: {filename}")

async def main():
    voice = "es-ES-AlvaroNeural"
    test_text = "[EPICO] Las estrellas son los ojos de la creación. [/EPICO]"
    
    translated = translate_emotions(test_text)
    
    # Case 1: Minimal <speak> (Current)
    ssml_minimal = wrap_ssml_minimal(translated)
    print(f"Minimal SSML: {ssml_minimal}")
    await test_audio(ssml_minimal, "debug_minimal.mp3", voice)
    
    # Case 2: Full <speak> (Alternative)
    ssml_full = wrap_ssml_full(translated, voice)
    print(f"Full SSML: {ssml_full}")
    await test_audio(ssml_full, "debug_full.mp3", voice)
    
    # Case 3: Character with special characters
    special_text = "[TENSO] 5 < 10 y 20 > 15 & algo [/TENSO]"
    translated_special = translate_emotions(special_text)
    ssml_special = wrap_ssml_minimal(translated_special)
    print(f"Special SSML: {ssml_special}")
    await test_audio(ssml_special, "debug_special.mp3", voice)

if __name__ == "__main__":
    asyncio.run(main())
