import os
import sys
import json

# Add current dir to path
sys.path.append(os.path.abspath("."))
from aivideogen.generator.avgl_engine import extract_subtitles_v35

def test_clipping_logic():
    print("--- Simulación de Lógica de Clipping v17.3.3 ---")
    
    # Escenario: Texto que se dice muy rápido
    # "Hola" (0.1s) + "Mundo" (0.1s). Pero el motor fuerza 1s min.
    # d_words = 15 para forzar split en 10 + 5
    text = "Uno dos tres cuatro cinco seis siete ocho nueve diez Once doce trece catorce quince"
    
    # Simulamos el word_timings ACELERADO (0.05s por palabra)
    # 10 palabras = 0.5s de duración real.
    # Pero el motor forzará s_dur = 1.0s.
    word_timings = []
    for i in range(15):
        word_timings.append({
            "start": i * 0.05, 
            "end": (i + 1) * 0.05,
            "word": "word"
        })
    
    _, subs = extract_subtitles_v35(text, force_dynamic=True)
    
    print(f"Chunks generados: {len(subs)}")
    
    # Simulamos el bucle de clipping de generate_video_avgl
    for idx, sub in enumerate(subs):
        s_start = word_timings[sub['offset']]['start']
        # Forzamos el problema: duracion minima de 1s
        s_dur = 1.0 
        
        y_pos = 0.70
        
        print(f"\nChunk {idx}: '{sub['text'][:30]}...'")
        print(f"  Inicio original: {s_start:.2f}s")
        print(f"  Fin original (con 1s min): {s_start + s_dur:.2f}s")
        
        # APLICAMOS LA LÓGICA DEL PARCHE
        if idx + 1 < len(subs):
            next_sub = subs[idx + 1]
            if next_sub.get('y_position', 0.70) == y_pos:
                next_start = word_timings[next_sub['offset']]['start']
                
                if s_start + s_dur > next_start:
                    s_dur = max(0.1, next_start - s_start)
                    print(f"  [FIX] SOLAPAMIENTO! Recortando a: {s_dur:.2f}s")
                    print(f"  Nuevo Fin: {s_start + s_dur:.2f}s (Coincide con inicio del next: {next_start:.2f}s)")
        
        if idx > 0:
            prev_start = word_timings[subs[idx-1]['offset']]['start']
            # Si el fin del anterior es mayor al inicio de este, hay error
            # (Pero aquí ya lo corregimos arriba)
            pass

if __name__ == "__main__":
    test_clipping_logic()
