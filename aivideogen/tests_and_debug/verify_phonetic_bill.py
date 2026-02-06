import sys
import os
import io

# Force UTF-8 for stdout/stderr to avoid encoding issues in terminal
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add the project root to sys.path
sys.path.append(r'c:\dell inspiron 15 3000\curso IA\aivideogen3\aivideogen')

# Mock Django settings if needed
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aivideogen.settings')

from generator.avgl_engine import extract_subtitles_v35

def test_phonetic_logic():
    print("--- Test 1: Simple PHO ---")
    text = "Las [PHO]inteligencias artificiales | IAs[/PHO] están cambiando el mundo."
    clean, subs = extract_subtitles_v35(text)
    print(f"Original: {text}")
    print(f"Narracion: {clean}")
    print(f"Subtitulos: {subs}")
    assert clean == "Las inteligencias artificiales están cambiando el mundo."
    assert subs[0]["text"] == "IAs"
    
    print("\n--- Test 2: Multiple Tags (SUB + PHO) ---")
    text = "[SUB]Hola[/SUB], las [PHO]inteligencias artificiales | IAs[/PHO] son [SUB: 1 | geniales]."
    clean, subs = extract_subtitles_v35(text)
    print(f"Narracion: {clean}")
    for i, s in enumerate(subs):
        print(f"Sub {i}: {s}")
    
    assert "Hola" in clean
    assert "inteligencias artificiales" in clean
    assert "geniales" in clean
    assert subs[1]["text"] == "IAs"

    print("\n--- Test 3: Robustness Check (No freezing) ---")
    text = "Probando [PHO] una cosa | otra [/PHO] con [SUB] espacios [/SUB] y [SIMPLE: tag] que no existe."
    clean, subs = extract_subtitles_v35(text)
    print(f"Narracion: {clean}")
    print(f"Subs: {subs}")

    print("\n--- VERIFICACION COMPLETADA CON EXITO ---")

if __name__ == "__main__":
    try:
        test_phonetic_logic()
    except Exception as e:
        print(f"Error en el test: {str(e)}")
        sys.exit(1)
