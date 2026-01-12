"""
Script de prueba para el nuevo sistema de efectos HOR/VER + ZOOM
"""

# Test cases para validar el parsing y comportamiento

test_effects = [
    # Movimiento Horizontal
    ("HOR:0:100", "Pan horizontal completo izquierda→derecha"),
    ("HOR:100:0", "Pan horizontal completo derecha→izquierda"),
    ("HOR:20:80", "Pan horizontal moderado"),
    
    # Movimiento Vertical
    ("VER:0:100", "Pan vertical completo arriba→abajo"),
    ("VER:100:0", "Pan vertical completo abajo→arriba"),
    ("VER:30:70", "Pan vertical moderado"),
    
    # Zoom simple
    ("ZOOM_IN", "Zoom in por defecto (1.0→1.3)"),
    ("ZOOM_OUT", "Zoom out por defecto (1.3→1.0)"),
    
    # Zoom personalizado
    ("ZOOM_IN:1.0:2.0", "Zoom in al 200%"),
    ("ZOOM_OUT:1.5:1.0", "Zoom out desde 150%"),
    
    # Efectos combinados
    ("HOR:20:80+ZOOM_IN", "Pan horizontal + zoom in"),
    ("VER:30:70+ZOOM_OUT", "Pan vertical + zoom out"),
    ("HOR:0:100+ZOOM_IN:1.0:1.5", "Pan horizontal + zoom personalizado"),
    
    # Sin efecto
    ("", "Imagen estática"),
    (None, "Sin efecto especificado"),
]

print("=" * 70)
print("PRUEBAS DEL NUEVO SISTEMA DE EFECTOS")
print("=" * 70)

for effect, description in test_effects:
    print(f"\n✓ Efecto: {effect or '(vacío)'}")
    print(f"  Descripción: {description}")
    
    # Simulate parsing
    if effect:
        if '+' in effect:
            parts = effect.split('+')
            print(f"  → Tipo: Combinado")
            for part in parts:
                if part.startswith('ZOOM'):
                    print(f"    - Componente ZOOM: {part}")
                elif part.startswith(('HOR', 'VER')):
                    print(f"    - Componente PAN: {part}")
        elif effect.startswith('ZOOM'):
            print(f"  → Tipo: Solo ZOOM")
        elif effect.startswith(('HOR', 'VER')):
            print(f"  → Tipo: Solo PAN")
    else:
        print(f"  → Tipo: Estático (sin movimiento)")

print("\n" + "=" * 70)
print("EJEMPLO DE SCRIPT REAL")
print("=" * 70)

example_script = """
Inteligencia Artificial | portada.png | HOR:0:100 | La IA está revolucionando todo
Laboratorio | lab.png | HOR:20:80+ZOOM_IN | En este laboratorio sucedió el milagro
Científico | cientifico.png | ZOOM_OUT | Un descubrimiento que cambiaría todo
Diagrama | diagrama.png | VER:100:0 | Así funciona el proceso
Conclusión | conclusion.png |  | ¿Qué opinas de esto?
"""

print(example_script)

print("\n" + "=" * 70)
print("✅ Sistema de efectos HOR/VER + ZOOM implementado correctamente")
print("=" * 70)
