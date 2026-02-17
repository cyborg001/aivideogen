import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'aivideogen')))

from aivideogen.generator.avgl_engine import extract_subtitles_v35
from aivideogen.generator.video_engine import render_pro_subtitles
from moviepy import ColorClip, CompositeVideoClip, TextClip, AudioFileClip

def generate_preview():
    print("[V16 PREVIEW] Iniciando generación de ejemplo...")
    
    # 1. Test Text (Architect's requirements)
    # 2. Mock Data: Párrafo denso para prueba v16.1
    text = "[SUB]¡Hola a todos![/SUB] Este es un test de los subtítulos v16.1 con resaltado dinámico. [SUB]Esto se supone que es un párrafo largo que debe dividirse en bloques automáticos para el modo cine.[/SUB]"
    duration = 8.0 # Suficiente para el párrafo
    # 2. Parse tags (Order: clean_text, raw_subs)
    clean_text, raw_subs = extract_subtitles_v35(text)
    print(f"   - Texto limpio: {clean_text}")
    print(f"   - Subtítulos detectados: {len(raw_subs)}")
    for s in raw_subs:
        print(f"     * [{s['text']}] (word_count: {s['word_count']})")

    # 3. Create Sample Video
    target_size = (1080, 1920) # Vertical Shorts format
    duration = 5.0
    
    # Background (Dark grey)
    bg = ColorClip(size=target_size, color=(30, 30, 30)).with_duration(duration)
    
    # 4. Render Subtitles using PRO Module
    sub_clips = []
    total_words = len(clean_text.split())
    
    # 4. Generate Subtitles with v16.3 MOVIE MODE logic
    sub_clips = []
    
    for s in raw_subs:
        if s['word_count'] <= 0:
            print(f"   - [PHO] Detectado: '{s['text']}'")
            continue
            
        # Segment timing
        s_text = s['text']
        s_start = (s['offset'] / total_words) * duration
        s_dur = (s['word_count'] / total_words) * duration
        
        # MOVIE MODE SIMULATION: Render the entire segment as a single block
        # In the real engine, this is triggered by 'movie_mode': True
        print(f"   - [MOVIE MODE] Renderizando bloque completo: '{s_text[:30]}...' @ {s_start:.2f}s")
        sub = render_pro_subtitles(s_text, s_dur, target_size, full_highlight=True)
        sub = sub.with_start(s_start)
        sub_clips.append(sub)
    
    # 5. Composite and Export
    print(f"   - Creando composición final con {len(sub_clips)} bloques de subtítulos...")
    final = CompositeVideoClip([bg] + sub_clips)
    
    # Ensure output directory exists
    os.makedirs("media", exist_ok=True)

    # 6. Debug: Save a Frame
    frame_path = "media/v16_debug_frame.png"
    print(f"   - [DEBUG] Guardando frame en t=1.0s para verificar visibilidad...")
    final.save_frame(frame_path, t=1.0)
    
    print(f"   - Renderizando video...")
    final.write_videofile("media/v16_preview.mp4", fps=24, codec='libx264')
    print(f"\n[V16 PREVIEW] ¡ÉXITO! Video generado en media/v16_preview.mp4")
    print(f"[V16 PREVIEW] Frame de debug guardado en {frame_path}")

if __name__ == "__main__":
    generate_preview()
