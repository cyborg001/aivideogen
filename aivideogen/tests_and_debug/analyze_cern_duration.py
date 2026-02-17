import json
import re

def analyze_script(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total_words = 0
    scenes_count = 0
    
    print(f"--- Análisis de Guion: {data.get('title')} ---")
    
    for block in data.get('blocks', []):
        for scene in block.get('scenes', []):
            scenes_count += 1
            text = scene.get('text', '')
            # Limpiar tags para contar solo palabras reales
            clean_text = re.sub(r'\[.*?\]', '', text)
            words = clean_text.split()
            total_words += len(words)
            
    # Estimación: 140 palabras por minuto (estándar para EmilioNeural)
    words_per_minute = 140
    duration_minutes = total_words / words_per_minute
    duration_seconds = duration_minutes * 60
    
    # Añadir un margen de 1.5s por escena para pausas y transiciones
    total_duration_real = duration_seconds + (scenes_count * 1.5)
    
    print(f"Total Escenas: {scenes_count}")
    print(f"Total Palabras: {total_words}")
    print(f"Duración Estimada Narrada: {duration_seconds:.1f} segundos")
    print(f"Duración Proyectada Total (con pausas): {total_duration_real:.1f} segundos")
    print(f"Duración en Formato: {int(total_duration_real // 60)}:{int(total_duration_real % 60):02d} minutos")

if __name__ == "__main__":
    analyze_script('c:/Users/hp/aivideogen/aivideogen/guiones/noticia_cern_v23.json')
