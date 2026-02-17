import os
import sys
import json

# Add current dir to path
sys.path.append(os.path.abspath("."))
from aivideogen.generator.avgl_engine import parse_avgl_json

def debug_json_subs(json_path):
    print(f"--- Depurando Subtítulos de: {os.path.basename(json_path)} ---")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        json_text = f.read()
        
    script = parse_avgl_json(json_text)
    
    for b_idx, block in enumerate(script.blocks):
        for s_idx, scene in enumerate(block.scenes):
            if b_idx == 0 and s_idx == 0:
                print(f"\nEscena {b_idx}.{s_idx}: {scene.title}")
                print(f"Texto original: {scene.text}")
                print(f"Cant. Subtítulos: {len(scene.subtitles)}")
                
                for i, sub in enumerate(scene.subtitles):
                    print(f"  [{i}] '{sub['text']}'")
                    print(f"      offset: {sub.get('offset')} | count: {sub.get('word_count')} | dyn: {sub.get('is_dynamic')}")

if __name__ == "__main__":
    path = "c:/Users/hp/aivideogen/aivideogen/guiones/showcase_dynamic_v16.json"
    if os.path.exists(path):
        debug_json_subs(path)
    else:
        print("Archivo no encontrado.")
