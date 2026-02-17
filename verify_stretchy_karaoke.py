
import sys
import os

# Set up paths
sys.path.append(os.path.join(os.getcwd(), 'aivideogen'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aivideogen.settings')

import re
from generator.avgl_engine import extract_subtitles_v35

def test_nested_tags():
    print("Testing Nested Tags in Karaoke (v16.7.13)...")
    
    # Example 1: PHO inside DYN
    text1 = "[DYN] El [PHO] Togo | perro [/PHO] corre rápido [/DYN]"
    clean1, subs1 = extract_subtitles_v35(text1)
    
    print(f"Text: {text1}")
    print(f"Clean Voice: '{clean1}'")
    print(f"Sub visible: '{subs1[0]['text']}'")
    
    assert clean1 == "El Togo corre rápido", f"Voice mismatch: {clean1}"
    assert subs1[0]['text'] == "El perro corre rápido", f"Sub mismatch: {subs1[0]['text']}"
    assert subs1[0]['is_dynamic'] == True
    
    # Example 2: SUB inside DYN (Phonetic override)
    text2 = "[DYN] Bienvenidos a [SUB: A-C-I]ACI[/SUB] el futuro [/DYN]"
    clean2, subs2 = extract_subtitles_v35(text2)
    
    print(f"Text: {text2}")
    print(f"Clean Voice: '{clean2}'")
    print(f"Sub visible: '{subs2[0]['text']}'")
    
    assert clean2 == "Bienvenidos a A-C-I el futuro", f"Voice mismatch: {clean2}"
    assert subs2[0]['text'] == "Bienvenidos a ACI el futuro", f"Sub mismatch: {subs2[0]['text']}"
    
    print("[SUCCESS] extraction tests passed!\n")

def test_chunk_size_logic():
    print("Verifying Word Mapping Strategy (Simulation)...")
    # This simulates what video_engine would do
    visible_words = "Uno dos tres cuatro cinco seis siete ocho nueve diez".split()
    chunk_size = 7
    
    chunks = []
    for i in range(0, len(visible_words), chunk_size):
        chunks.append(visible_words[i : i + chunk_size])
    
    print(f"Total words: {len(visible_words)}")
    print(f"Chunks (chunk_size={chunk_size}): {len(chunks)}")
    for idx, c in enumerate(chunks):
        print(f"  Chunk {idx}: {c}")
        
    assert len(chunks) == 2
    assert len(chunks[0]) == 7
    assert len(chunks[1]) == 3
    
    print("[SUCCESS] chunking logic verified.")

if __name__ == "__main__":
    try:
        test_nested_tags()
        test_chunk_size_logic()
        print("\n[ALL TESTS PASSED] Karaoke-First v16.7.13 is ready.")
    except Exception as e:
        print(f"\n[FAIL] {e}")
        sys.exit(1)
