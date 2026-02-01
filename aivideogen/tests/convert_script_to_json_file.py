import os
import json
from generator.avgl_engine import convert_text_to_avgl_json

INPUT_FILE = r'c:\Users\Usuario\Documents\curso creacion contenido con ia\articulos\guion_ces_2026.md'
OUTPUT_FILE = r'c:\Users\Usuario\Documents\curso creacion contenido con ia\guiones\ces_2026_special_v4.json'

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Input file not found: {INPUT_FILE}")
        return

    try:
        # Read raw text
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            text_content = f.read()

        # Convert using existing engine logic
        # We pass a custom title
        avgl_data = convert_text_to_avgl_json(text_content, title="CES 2026 Special (JSON)")
        
        # Override Voice to Dominican as requested
        avgl_data['voice'] = "es-DO-EmilioNeural"
        avgl_data['speed'] = 1.1 # +10% roughly
        
        # Validate critical fields manually
        print(f"✅ Converted {len(avgl_data['blocks'][0]['scenes'])} scenes.")
        
        # Check overlays
        overlap_count = 0
        for scene in avgl_data['blocks'][0]['scenes']:
            for asset in scene['assets']:
                if asset.get('overlay'):
                    overlap_count += 1
                    print(f"  ✨ Overlay found: {asset['overlay']} in scene '{scene['title']}'")

        # Save to JSON
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(avgl_data, f, indent=4, ensure_ascii=False)
            
        print(f"🚀 Successfully saved JSON to: {OUTPUT_FILE}")

    except Exception as e:
        print(f"❌ Error converting script: {e}")

if __name__ == "__main__":
    main()
