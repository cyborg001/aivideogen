
import re
import xml.sax.saxutils as saxutils

def translate_emotions_v1(text):
    """CURRENT BROKEN IMPLEMENTATION"""
    emotions = {'EPICO': {'pitch': '+5Hz'}}
    processed_text = text
    for tag, attrs in emotions.items():
        pattern = rf'\[{tag}\](.*?)\[/{tag}\]'
        attr_str = " ".join([f'{k}="{v}"' for k, v in attrs.items()])
        def replace_with_ssml(match):
            return f'<prosody {attr_str}>{saxutils.escape(match.group(1))}</prosody>'
        processed_text = re.sub(pattern, replace_with_ssml, processed_text, flags=re.IGNORECASE | re.DOTALL)
    return processed_text

def translate_emotions_v2(text):
    """PROPOSED FIX: Escape everything first"""
    emotions = {'EPICO': {'pitch': '+5Hz'}}
    
    # 1. Escape the whole text first
    # This handles "5 < 10" becoming "5 &lt; 10"
    processed_text = saxutils.escape(text)
    
    for tag, attrs in emotions.items():
        # 2. MATCH ESCAPED TAGS?
        # saxutils.escape does NOT escape [ or ]
        pattern = rf'\[{tag}\](.*?)\[/{tag}\]'
        attr_str = " ".join([f'{k}="{v}"' for k, v in attrs.items()])
        
        # 3. Simple replacement (content is already escaped)
        replacement = rf'<prosody {attr_str}>\1</prosody>'
        processed_text = re.sub(pattern, replacement, processed_text, flags=re.IGNORECASE | re.DOTALL)
        
    return processed_text

def wrap_ssml(text):
    if '<prosody' in text:
         return f'<speak>{text}</speak>'
    return text

bad_input = "Hola < mundo. [EPICO]Esto es épico[/EPICO]"

print("--- V1 (Current) ---")
res_v1 = translate_emotions_v1(bad_input)
print(f"Result: {res_v1}")
final_v1 = wrap_ssml(res_v1)
print(f"Final XML: {final_v1}")
# Expected V1: "Hola < mundo. <prosody...>Esto es épico</prosody>" -> INVALID XML inside <speak>

print("\n--- V2 (Proposed) ---")
res_v2 = translate_emotions_v2(bad_input)
print(f"Result: {res_v2}")
final_v2 = wrap_ssml(res_v2)
print(f"Final XML: {final_v2}")
# Expected V2: "Hola &lt; mundo. <prosody...>Esto es épico</prosody>" -> VALID XML
