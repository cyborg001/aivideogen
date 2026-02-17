
import sys
import os
import django

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# No need for django setup for this pure function test

from aivideogen.generator.avgl_engine import extract_subtitles_v35

def test_sub_fix():
    text = "[SUB: La Saga Alpha][TENSO]Sabías que Google ya no solo juega ajedrez... [/TENSO]"
    fonetica, subs = extract_subtitles_v35(text)
    
    print(f"Fonetica Final: '{fonetica}'")
    print("Subtítulos:")
    for s in subs:
        print(f" - {s}")

if __name__ == "__main__":
    test_sub_fix()
