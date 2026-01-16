import json
import re

# COPIED LOGIC FROM avgl_engine.py TO AVOID DJANGO DEPENDENCY ISSUES
def translate_emotions(text):
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
    if '<prosody' in text or '<break' in text:
        return f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="es-ES"><voice name="{voice}"><prosody rate="{speed}">{text}</prosody></voice></speak>'
    return text

def parse_avgl_json_simplified(json_text):
    data = json.loads(json_text)
    return data

def debug_file(file_path):
    print(f"📂 Leyendo archivo: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    print(f"✅ Archivo leído. Parseando JSON...")
    
    try:
        data = parse_avgl_json_simplified(content)
        title = data.get("title", "Video Sin Título")
        voice_global = data.get("voice", "es-ES-AlvaroNeural")
        speed_global = data.get("speed", 1.0)
        
        print(f"🎬 Título del Video: {title}")
        print(f"🗣️  Voz Global: {voice_global}")
        print("-" * 50)
        
        blocks = data.get("blocks", [])
        scene_count = 0
        
        for block in blocks:
            for scene in block.get("scenes", []):
                scene_count += 1
                title = scene.get("title", "Sin Título")
                text = scene.get("text", "")
                voice = scene.get("voice", voice_global)
                speed = scene.get("speed", speed_global)
                
                print(f"\n--- ESCENA {scene_count}: {title} ---")
                print(f"📝 Texto Original (JSON):")
                print(f"   '{text}'")
                
                text_with_emotions = translate_emotions(text)
                if text_with_emotions != text:
                    print(f"✨ Texto con Emociones/Pausas:")
                    print(f"   '{text_with_emotions}'")
                
                speed_rate = f"+{int((speed - 1.0) * 100)}%"
                ssml = wrap_ssml(text_with_emotions, voice, speed_rate)
                
                print(f"📤 LO QUE SE MANDA A EDGE-TTS (SSML):")
                if ssml.startswith('<speak'):
                    print(f"   {ssml}")
                else:
                    print(f"   (Texto plano)")
                    print(f"   '{ssml}'")
                    print(f"   [Parametro rate='{speed_rate}' se pasará aparte]")

    except Exception as e:
        print(f"❌ ERROR al procesar: {e}")

if __name__ == "__main__":
    target_file = r"c:\Users\Usuario\Documents\curso creacion contenido con ia\aivideogen3\aivideogen\docs\EJEMPLOS\guion_ejemplo_ia_v4.json"
    debug_file(target_file)
