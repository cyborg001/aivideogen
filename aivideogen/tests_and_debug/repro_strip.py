import re
import xml.sax.saxutils as saxutils

ACTIONS_CONFIG = {
    '[TOS]': 'cof, cof...',
    '[AJEM]': 'ajem...',
}

def deep_strip(t):
    """Aggressive cleanup of technical tags and stage directions (v4.7.1)"""
    # 1. Standard bracketed/parenthetical tags
    t = re.sub(r'\(.*?\)', '', t, flags=re.DOTALL)
    t = re.sub(r'\[.*?\]', '', t, flags=re.DOTALL)
    t = re.sub(r'<.*?>', '', t, flags=re.DOTALL)
    
    # 2. Selective unclosed/stray markers (v4.7.1: High stability)
    t = re.sub(r'^\s*\]+|\[+\s*$', '', t)
    
    # 3. Technical Leakage Cleanup (Raw text patterns like "SPEED: +10%")
    # This catches instructions that lost their brackets but shouldn't be read.
    # v4.7.2: Consume until end of line/segment to avoid leaving residue like "10 %"
    t = re.sub(r'(?i)\b(SPEED|ZOOM|FIT|AUDIO|PAUSE|SFX|OVERLAY|MOVE|PAN|VOICE|PITCH|TITLE|INSTRUCCIÓN|INSTRUCTION)\s*:.*', '', t)
    
    # 4. Cleanup trailing colons or separators left behind
    t = re.sub(r'\s*[:|]+\s*$', '', t)
    
    return t.strip()

test_cases = [
    "[NARRADOR] [SPEED: +10%] Hola mundo",
    "Hola [SFX: boom] amigo",
    "[ETHAN] (Hablando bajo) Shhh",
    "Prueba con [SPEED: 1.1] y [TOS]",
    "<prosody rate='+10%'>Hola</prosody>",
    "[[SPEED: 1.1]] Doble",
    "[SPEED: +10% ] Espacio",
    "ZOOM: 1.0:1.3 Hola",
    "SPEED: 10 % Separado",
    "MOVE: HOR: 50 : 50 Espaciado",
    "AUDIO: c:/path/to/file.mp3 Algo mas",
    "ZOOM: 1.2, 1.3 Comas",
]

for text in test_cases:
    print(f"Original: {text}")
    # Simulate segment logic simplified
    # (Assuming everything is 'plain' to test deep_strip)
    content = text
    # Action translation
    for action_tag, onomatopoeia in ACTIONS_CONFIG.items():
        content = re.sub(re.escape(action_tag), onomatopoeia, content, flags=re.IGNORECASE)
    
    clean = deep_strip(content)
    print(f"Cleaned:  '{clean}'")
    print("-" * 20)
