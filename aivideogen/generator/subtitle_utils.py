import os
import pysubs2
from pysubs2 import SSAEvent, SSAStyle, make_time

def compile_full_script_ass(all_subtitles, output_path):
    """
    Genera un archivo .ass profesional usando pysubs2.
    all_subtitles: Lista de objetos { 'text', 'start', 'end', 'is_dynamic', 'y_pos', 'relevant_timings' }
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        subs = pysubs2.SSAFile()

        # 0. Configuración de Resolución Base (v26.1)
        # Esto asegura que los tamaños de fuente y márgenes sean consistentes 
        # independientemente de la resolución del video final.
        subs.info["PlayResX"] = 1080
        subs.info["PlayResY"] = 1920 # Default Portrait (Saga Alpha Standard)
        
        # 1. Definir Estilos Premium (Saga Alpha)
        # Estilo Principal (Bottom)
        style_main = SSAStyle()
        style_main.fontname = "Arial"
        style_main.fontsize = 50 # Incrementado para 1080x1920
        style_main.primarycolor = pysubs2.Color(255, 255, 255) # Blanco
        style_main.secondarycolor = pysubs2.Color(255, 255, 0) # Amarillo (para Karaoke)
        style_main.outlinecolor = pysubs2.Color(0, 0, 0) # Negro
        style_main.backcolor = pysubs2.Color(0, 0, 0, 128) # Sombra semi-transparente
        style_main.bold = True
        style_main.outline = 3.0
        style_main.shadow = 2.0
        style_main.alignment = 2 # Bottom Center
        style_main.marginv = 150 # Margen ampliado para seguridad
        subs.styles["AlphaMain"] = style_main

        # Estilo Título (Top)
        style_title = SSAStyle()
        style_title.fontname = "Arial"
        style_title.fontsize = 65
        style_title.primarycolor = pysubs2.Color(255, 215, 0) # Dorado/Amarillo
        style_title.outlinecolor = pysubs2.Color(0, 0, 0)
        style_title.bold = True
        style_title.outline = 4.0
        style_title.alignment = 8 # Top Center
        style_title.marginv = 200
        subs.styles["AlphaTitle"] = style_title

        # 2. Agregar Eventos
        for sub in all_subtitles:
            event = SSAEvent()
            # Convertir segundos a milisegundos para pysubs2
            event.start = int(sub['start'] * 1000)
            event.end = int(sub['end'] * 1000)
            
            # v26.6: Dynamic Vertical Positioning (Respect y_pos)
            y_pos = sub.get('y_pos', 0.70)
            
            if y_pos < 0.6:
                event.style = "AlphaTitle"
                # Top Alignment (an8) -> MarginV = y_pos * Height
                # e.g. 0.35 * 1920 = 672px from top
                event.marginv = int(y_pos * 1920)
            else:
                event.style = "AlphaMain"
                # Bottom Alignment (an2) -> Default Style Margin (150px = ~8%)
                # We stick to the fixed style for main subtitles to ensure consistency/safety
                # unless a specific override logic is needed later.

            
            text = sub['text']
            # Quitar etiquetas SRT legacy si existen
            text = text.replace('{\\an8}', '').replace('{\\an2}', '').strip()
            
            # Karaoke Dinámico [DYN]
            if sub.get('is_dynamic') and sub.get('relevant_timings'):
                # En ASS, el karaoke usa {\k<duracion_en_centisegundos>}
                # Pero para un resaltado simple palabra por palabra compatible con FFmpeg sin scripts complejos,
                # a veces es más robusto usar el método de fragmentación si el filtro simple falla.
                # Sin embargo, pysubs2 permite construir la línea de karaoke.
                karaoke_parts = []
                for w in sub['relevant_timings']:
                    # duracion en centisegundos (10ms cada unidad)
                    dur_cs = int((w['end'] - w['start']) * 100)
                    karaoke_parts.append(f"{{\\k{dur_cs}}}{w['word']} ")
                event.text = "".join(karaoke_parts).strip()
            else:
                event.text = text
            
            subs.append(event)

        subs.save(output_path)
        return True
    except Exception as e:
        print(f"Error generando ASS con pysubs2: {e}")
        import traceback
        traceback.print_exc()
        return False
