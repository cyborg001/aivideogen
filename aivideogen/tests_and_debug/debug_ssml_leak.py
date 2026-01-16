
import re

def translate_emotions(text):
    """
    Translates custom emotion tags like [TENSO] into SSML prosody tags.
    """
    emotions = {
        'TENSO': {'pitch': '-10Hz', 'rate': '-15%'},
        'EPICO': {'pitch': '+5Hz', 'rate': '+10%', 'volume': '+15%'},
        'SUSPENSO': {'pitch': '-5Hz', 'rate': '-25%'},
        'GRITANDO': {'pitch': '+15Hz', 'rate': '+20%', 'volume': 'loud'},
        'SUSURRO': {'pitch': '-12Hz', 'rate': '-20%', 'volume': '-30%'},
    }
    
    processed_text = text
    for tag, attrs in emotions.items():
        pattern = rf'\[{tag}\](.*?)\[/{tag}\]'
        attr_str = " ".join([f'{k}="{v}"' for k, v in attrs.items()])
        replacement = rf'<prosody {attr_str}>\1</prosody>'
        processed_text = re.sub(pattern, replacement, processed_text, flags=re.IGNORECASE | re.DOTALL)
    
    # Process [PAUSA:X.X] -> <break time="X.Xs"/>
    processed_text = re.sub(r'\[PAUSA:([\d\.]+)\]', r'<break time="\1s"/>', processed_text, flags=re.IGNORECASE)
    
    return processed_text


def wrap_ssml(text, voice, speed="+0%"):
    """
    Wraps text in SSML tags if necessary.
    """
    if '<prosody' in text or '<break' in text:
        content = text
        if speed != "+0%":
            content = f'<prosody rate="{speed}">{text}</prosody>'
        return f'<speak>{content}</speak>'
    return text

# Test cases
test_texts = [
    "[EPICO] La información fluye a la velocidad de la luz. [/EPICO]",
    "Texto normal sin etiquetas",
    "[SUSPENSO] Algo se acerca... [PAUSA:1.0] muy rápido. [/SUSPENSO]",
    "[TENSO] Cuidado con los caracteres especiales como < & > [/TENSO]",
    "Texto [ROTO] que no es un tag [/ROTO]"
]

print("--- DEBUG SSML LEAKAGE ---")
for t in test_texts:
    translated = translate_emotions(t)
    final = wrap_ssml(translated, "es-ES-AlvaroNeural", "+0%")
    print(f"\nOriginal: {t}")
    print(f"Translated: {translated}")
    print(f"Final SSML: {final}")
