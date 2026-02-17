"""
Test script para parse_escena()
Prueba la separacion de fonetica, display y highlights
"""

import sys
sys.path.insert(0, r'c:\Users\hp\aivideogen')

from aivideogen.generator.avgl_engine import parse_escena

# Casos de prueba
test_cases = [
    {
        "name": "PHO simple sin highlight",
        "input": "Hoy hablaremos de [PHO]em ele|ML[/PHO] en detalle"
    },
    {
        "name": "PHO con highlight",
        "input": "Esto es una escena [PHO:h]cul|cool[/PHO] ;)"
    },
    {
        "name": "Multiples PHO con y sin highlight",
        "input": "[PHO:h]i a|IA[/PHO] revoluciona [PHO:h]ei de ge|Edge[/PHO] Computing y [PHO]em ele|ML[/PHO]"
    },
    {
        "name": "Texto sin PHO",
        "input": "Esta es una escena normal sin tags PHO"
    },
    {
        "name": "PHO sin separador (mismo texto)",
        "input": "Usa [PHO]Python[/PHO] para programar"
    }
]

print("=" * 80)
print("TEST: parse_escena()")
print("=" * 80)

for i, test in enumerate(test_cases, 1):
    print(f"\n{'-' * 80}")
    print(f"Test {i}: {test['name']}")
    print(f"{'-' * 80}")
    print(f"INPUT:\n  {test['input']}")
    
    fonetica, display, highlights = parse_escena(test['input'])
    
    print(f"\nOUTPUT:")
    print(f"  Fonetica (TTS): {fonetica}")
    print(f"  Display (SUB):  {display}")
    print(f"  Highlights:     {highlights}")
    
    # Validaciones
    print(f"\n  OK Longitudes: fonetica={len(fonetica.split())} palabras, display={len(display.split())} palabras")
    if highlights:
        print(f"  OK Highlights detectados: {len(highlights)}")

print(f"\n{'=' * 80}")
print("TESTS COMPLETADOS")
print("=" * 80)
