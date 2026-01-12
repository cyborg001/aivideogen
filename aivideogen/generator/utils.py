import requests
import os
import numpy as np
import random
import asyncio
import json
import re
import xml.etree.ElementTree as ET
from django.conf import settings
from django.utils.text import slugify

class AVGLEvent:
    """Represents an in-line event (sfx, asset change, ambient, etc.)"""
    def __init__(self, type, params, offset_words=0):
        self.type = type # 'sfx', 'asset', 'ambient', 'voice_change', etc.
        self.params = params
        self.offset_words = offset_words # Words from start of scene text
        self.start_time = 0 # To be calculated after TTS duration

class AVGLScene:
    """Represents a full scene block in AVGL"""
    def __init__(self, title):
        self.title = title
        self.clean_text = ""
        self.events = []
        self.base_voice = None # es-ES-AlvaroNeural, etc.
        self.music = None # Inherited or specific

class AVGLBlock:
    """Represents a group of scenes with common settings (like music)"""
    def __init__(self, title, music=None):
        self.title = title
        self.music = music
        self.scenes = []

class AVGLScript:
    """The root container for the entire script"""
    def __init__(self, title):
        self.title = title
        self.blocks = []

    def get_all_scenes(self):
        """Helper to flatten hierarchy for analysis/parsing"""
        all_scenes = []
        for block in self.blocks:
            all_scenes.extend(block.scenes)
        return all_scenes

def parse_avgl_script(script_text):
    """
    Parses a script in AVGL format into an AVGLScript object (Tree structure).
    Hierarchy: <avgl> -> <bloque> -> <scene>
    """
    # 1. Root Level: <avgl title="...">
    root_match = re.search(r'<avgl\s+title="([^"]+)"\s*>(.*?)</avgl>', script_text, re.DOTALL | re.IGNORECASE)
    if not root_match:
        # Fallback for simple scripts or legacy scenes without root
        script_title = "Video Sin Título"
        inner_content = script_text
    else:
        script_title = root_match.group(1)
        inner_content = root_match.group(2)

    script = AVGLScript(script_title)

    # 2. Block Level: <bloque title="..." music="...">
    block_matches = re.finditer(r'<bloque\s+([^>]*?)>(.*?)</bloque>', inner_content, re.DOTALL | re.IGNORECASE)
    
    found_blocks = False
    for b_match in block_matches:
        found_blocks = True
        attr_str = b_match.group(1)
        b_content = b_match.group(2)
        
        # Parse block attributes
        b_attrs = {}
        for attr_match in re.finditer(r'(\w+)="([^"]*)"', attr_str):
            b_attrs[attr_match.group(1).lower()] = attr_match.group(2)
        
        block = AVGLBlock(title=b_attrs.get('title', 'Bloque Sin Título'), 
                         music=b_attrs.get('music'))
        
        # 3. Scene Level: <scene title="...">
        scene_matches = re.finditer(r'<scene\s+title="([^"]+)"\s*>(.*?)</scene>', b_content, re.DOTALL | re.IGNORECASE)
        for s_match in scene_matches:
            scene = AVGLScene(s_match.group(1))
            scene.music = block.music # Target inheritance
            
            # Parse events and text inside scene
            _process_scene_content(scene, s_match.group(2))
            block.scenes.append(scene)
        
        script.blocks.append(block)

    if not found_blocks:
        # Fallback: Process scenes at top level if no blocks found
        dummy_block = AVGLBlock("Bloque Unico")
        scene_matches = re.finditer(r'<scene\s+title="([^"]+)"\s*>(.*?)</scene>', inner_content, re.DOTALL | re.IGNORECASE)
        for s_match in scene_matches:
            scene = AVGLScene(s_match.group(1))
            _process_scene_content(scene, s_match.group(2))
            dummy_block.scenes.append(scene)
        script.blocks.append(dummy_block)

    return script

def _process_scene_content(scene, content):
    """Utility to process tags and text inside a scene block"""
    parts = re.split(r'(<[^>]+>)', content)
    word_accumulator = []
    for part in parts:
        if not part: continue
        if part.startswith('<') and not part.startswith('</'):
            tag_match = re.match(r'<(\w+)\s*([^>]*?)(/?)>', part)
            if tag_match:
                tag_name = tag_match.group(1).lower()
                attr_str = tag_match.group(2)
                is_self_closing = tag_match.group(3) == '/' or tag_name in ['asset', 'sfx', 'ambient', 'music', 'pause', 'camera', 'overlay']
                
                attrs = {}
                for attr_match in re.finditer(r'(\w+)="([^"]*)"', attr_str):
                    attrs[attr_match.group(1).lower()] = attr_match.group(2)
                
                offset = len(" ".join(word_accumulator).split())
                event = AVGLEvent(tag_name, attrs, offset)
                scene.events.append(event)
        elif not part.startswith('</'):
            clean_p = part.strip()
            if clean_p:
                word_accumulator.append(clean_p)
                scene.clean_text += " " + clean_p
    scene.clean_text = scene.clean_text.strip()


def generate_script_ai(news_item):
    """
    Generates a high-impact script and visual prompts for a news item using Gemini API.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None, "Error: No se encontró GEMINI_API_KEY en las variables de entorno.", None

    prompt = f"""
Eres un director y guionista experto en YouTube Shorts para el canal "Noticias de IA y ciencias".
Tu objetivo es transformar la noticia adjunta en un guion CINEMATOGRÁFICO de alto impacto (máx 2.5 min).

Escribe el guion en el nuevo lenguaje AVGL v3.0 (AI Video Generation Language).
No uses columnas ni tablas. Usa etiquetas estructuradas.

ESTRUCTURA AVGL:
1. Cada escena se abre con <scene title="Nombre de la Escena"> y se cierra con </scene>.
2. Dentro de cada escena DISPARA LOS ACTIVOS:
   - <asset type="imagen.png" zoom="1.0:1.2" move="HOR:0:100" overlay="glitch" />
3. DISPARA LOS EFECTOS DE SONIDO:
   - <sfx type="impacto" volume="0.5" />
4. DISPARA LOS SILENCIOS:
   - <pause duration="1.5" />
6. CONTROL DE MÚSICA POR BLOQUES:
   - <bloque music="nombre_pista" volume="0.2" />
   - Úsalo al inicio de cada parte o capítulo del video para cambiar la atmósfera.
7. CONTROL DE VOZ (Opcional):
   - <voice name="NombreVoz"> Texto </voice>
   - Usa etiquetas de emoción como [TENSO], [EPICO], [SUSPENSO] para envolver frases clave.

REGLAS CRÍTICAS:
- El Hook (0-2s) debe ser impactante.
- Cambia el activo visual (<asset />) al menos 3 veces por cada 15 segundos para dar ritmo.
- No uses negritas ni carácteres extraños.
- El final debe ser la frase: "Y recuerda... ¡el futuro es hoy!".

DATOS DE LA NOTICIA:
Título: {news_item.title}
Resumen: {news_item.summary}
Fuente: {news_item.source.name}

RESPUESTA REQUERIDA (Formato JSON):
Responde con un objeto JSON con:
1. "script": El guion completo en formato AVGL.
2. "prompts": Lista de objetos con "file" y "prompt" técnico detallado.
3. "music_suggestion": Estilo de música ideal.
4. "hashtags": Lista de 10-12 hashtags sugeridos (4 marca, 4 tema, 4 contenido).

Responde ÚNICAMENTE el JSON.
"""

    model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1/models/{model_name}:generateContent?key={api_key}"
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            content = result['candidates'][0]['content']['parts'][0]['text']
            # Extract JSON from markdown code blocks if present
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            elif '```' in content:
                # Remove any code fences
                content = re.sub(r'```\w*\n?', '', content)
            
            import json
            data = json.loads(content.strip())
            
            # Extract hashtags if present and format them
            hashtags_list = data.get('hashtags', [])
            if hashtags_list:
                hashtags_str = " ".join(hashtags_list)
            else:
                hashtags_str = ""
            
            # Return script, prompts (including hashtags), and music
            prompts_data = data.get('prompts', [])
            music_suggestion = data.get('music_suggestion', '')
            
            # Combine prompts with hashtags and music for display
            combined_prompts = {
                'prompts': prompts_data,
                'music': music_suggestion,
                'hashtags': hashtags_str
            }
            
            return data.get('script'), combined_prompts, music_suggestion
        else:
            human_msg = "No se pudo conectar con la IA. Por favor, asegúrate de que tu 'GEMINI_API_KEY' en el archivo '.env' sea válida y que tengas saldo en tu cuenta de Google AI Studio."
            return None, f"⚠️ {human_msg} (Error {response.status_code})", None
    except Exception as e:
        human_msg = "Parece que hay un problema de conexión o configuración. Revisa que tu internet funcione correctamente y que el nombre del modelo en el archivo '.env' sea el correcto."
        return None, f"🛑 {human_msg} (Detalle: {str(e)})", None

class ProjectLogger:
    def __init__(self, project):
        self.project = project
        self.log_buffer = []

    def log(self, message):
        import sys
        print(f"[Project {self.project.id}] {message}")
        # Force flush for PyInstaller executable
        sys.stdout.flush()
        sys.stderr.flush()
        self.log_buffer.append(message)
        self.project.log_output = "\n".join(self.log_buffer)
        self.project.save(update_fields=['log_output'])

async def generate_audio_edge(text, output_path, voice="es-ES-AlvaroNeural", rate="+0%"):
    import edge_tts
    try:
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        await communicate.save(output_path)
        return True
    except Exception as e:
        print(f"Error in generate_audio_edge: {e}")
        return False

async def generate_audio_elevenlabs(text, output_path, voice_id, api_key):
    from elevenlabs.client import ElevenLabs
    from elevenlabs import save
    try:
        client = ElevenLabs(api_key=api_key)
        audio_gen = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2"
        )
        save(audio_gen, output_path)
        return True
    except Exception as e:
        print(f"Error in generate_audio_elevenlabs: {e}")
        return False

def apply_ken_burns_effect(image_path, target_size, duration, effect=None):
    from moviepy import ImageClip, CompositeVideoClip
    
    img_clip = ImageClip(image_path).with_duration(duration)
    w_orig, h_orig = img_clip.size
    w_target, h_target = target_size
    
    # 1. Parse effects (AVGL Dictionary or Legacy String)
    hor_effect = ver_effect = zoom_effect = overlay_effect = None
    
    if isinstance(effect, dict):
        # AVGL Format
        hor_effect = effect.get('move') if effect.get('move') and 'HOR' in effect.get('move').upper() else None
        ver_effect = effect.get('move') if effect.get('move') and 'VER' in effect.get('move').upper() else None
        zoom_val = effect.get('zoom')
        if zoom_val:
            zoom_effect = f"ZOOM:{zoom_val}"
        overlay_effect = effect.get('overlay')
    elif isinstance(effect, str):
        # Legacy Format
        for p in effect.split('+'):
            p = p.strip()
            if p.startswith('HOR'): hor_effect = p
            elif p.startswith('VER'): ver_effect = p
            elif p.startswith('ZOOM'): zoom_effect = p
            elif p.startswith('OVERLAY'): overlay_effect = p

    # 2. Base Scale (Cover or Fit AR)
    scale_w = w_target / w_orig
    scale_h = h_target / h_orig
    
    # NEW: FIT mode support (v2.23.0)
    # v3.0 Alpha: Handle both legacy string effect and new dictionary parameters
    if isinstance(effect, dict):
        # Extract keywords from the whole dict (zoom, move, overlay, etc.)
        effect_str = " ".join([f"{k}:{v}" for k, v in effect.items()]).upper()
    else:
        effect_str = str(effect).upper() if effect else ""

    is_fit = 'FIT' in effect_str
    if is_fit:
        base_scale = min(scale_h, scale_w)
    else:
        base_scale = max(scale_h, scale_w)
    
    # 3. Smart Slack (v2.21.5) - Avoid over-zooming on orientation mismatch
    # Reduced from 1.3 to 1.15 for more professional/subtle look
    slack_factor = 1.15 
    
    # Add slack only where needed (if the axis doesn't have it naturally)
    needs_zoom_for_pan = False
    if hor_effect and scale_w >= (base_scale * 0.99): # Constrained horizontally
        needs_zoom_for_pan = True
    if ver_effect and scale_h >= (base_scale * 0.99): # Constrained vertically
        needs_zoom_for_pan = True
        
    if needs_zoom_for_pan:
        base_scale *= slack_factor

    # 3. Dynamic Functions
    def get_frame_scale(t):
        if not zoom_effect:
            return base_scale
        
        progress = t / duration
        # Default zoom range for simplified syntax
        zs, ze = 1.0, 1.3
        
        zp = zoom_effect.split(':')
        z_type = zp[0].strip()
        
        # Backward compatibility for ZOOM_IN/OUT
        if z_type == 'ZOOM_OUT':
            zs, ze = 1.3, 1.0
        
        # Override with custom values if provided: ZOOM:1.0:1.5 or ZOOM_IN:1.2:1.8
        try:
            if len(zp) >= 2 and zp[1].strip(): zs = float(zp[1])
            if len(zp) >= 3 and zp[2].strip(): ze = float(zp[2])
        except: pass
            
        rel_zoom = zs + (ze - zs) * progress
        return base_scale * rel_zoom

    def get_frame_pos(t):
        progress = t / duration
        # Use current scale to find current pixel dimensions
        scale = get_frame_scale(t)
        w_curr = w_orig * scale
        h_curr = h_orig * scale
        
        # Current available slack (overflow)
        slack_x = w_curr - w_target
        slack_y = h_curr - h_target
        
        # Default: Center
        x = -slack_x / 2
        y = -slack_y / 2
        
        # Horizontal (0% = Left, 100% = Right)
        if hor_effect:
            hp = hor_effect.split(':')
            try:
                h_start = float(hp[1]) if len(hp) >= 2 and hp[1].strip() else 0.0
                h_end = float(hp[2]) if len(hp) >= 3 and hp[2].strip() else 100.0
            except:
                h_start, h_end = 0.0, 100.0
            h_prog = h_start + progress * (h_end - h_start)
            x = -(h_prog / 100.0) * slack_x
            
        # Vertical (100% = Top, 0% = Bottom)
        if ver_effect:
            vp = ver_effect.split(':')
            try:
                v_start = float(vp[1]) if len(vp) >= 2 and vp[1].strip() else 0.0
                v_end = float(vp[2]) if len(vp) >= 3 and vp[2].strip() else 100.0
            except:
                v_start, v_end = 0.0, 100.0
            v_prog = v_start + progress * (v_end - v_start)
            y = -((100.0 - v_prog) / 100.0) * slack_y
            
        return (int(x), int(y))

    # Apply transformations frame-by-frame
    final_clip = img_clip.resized(get_frame_scale).with_position(get_frame_pos)
    
    # 4. Apply Overlay (New in v3.0 Alpha)
    if overlay_effect:
        try:
            overlay_file = overlay_effect.strip()
            if not overlay_file.lower().endswith('.mp4'): overlay_file += '.mp4'
            overlay_path = os.path.join(settings.MEDIA_ROOT, 'overlays', overlay_file)
            
            if os.path.exists(overlay_path):
                from moviepy import VideoFileClip
                ov_clip = VideoFileClip(overlay_path).resized(target_size)
                
                # Looping
                if ov_clip.duration < duration:
                    from moviepy import concatenate_videoclips
                    ov_loops = int(duration / ov_clip.duration) + 1
                    ov_clip = concatenate_videoclips([ov_clip] * ov_loops, method="chain")
                
                ov_clip = ov_clip.subclipped(0, duration).without_audio()
                ov_clip = ov_clip.with_mask(ov_clip.to_mask()).with_opacity(0.4)
                
                # Composite
                from moviepy import CompositeVideoClip
                final_clip = CompositeVideoClip([final_clip, ov_clip], size=target_size)
        except Exception as e:
            print(f"Warning: Failed to apply overlay '{overlay_effect}': {e}")

    # Wrap in CompositeVideoClip to maintain fixed output resolution
    return CompositeVideoClip([final_clip], size=target_size, bg_color=(0, 0, 0)).with_duration(duration)

def extract_hashtags_from_script(script_text):
    """
    Extracts hashtags from lines starting with # HASHTAGS:
    Returns a space-separated string of hashtags.
    """
    if not script_text:
        return ""
    
    tags = []
    for line in script_text.strip().split('\n'):
        line = line.strip()
        # More flexible check: any comment line containing HASHTAGS:
        if line.startswith('#') and 'HASHTAGS:' in line.upper():
            # Extract hashtags: # HASHTAGS: #tag1 #tag2
            parts = line.split(':', 1)
            if len(parts) > 1:
                # Find all words starting with #
                line_tags = [t.strip() for t in parts[1].split() if t.strip().startswith('#')]
                tags.extend(line_tags)
    
    return " ".join(tags)

def extract_sources_from_script(script_text):
    """
    Extracts sources from lines starting with # FUENTES:
    Returns a comma-separated string of sources.
    """
    if not script_text:
        return ""
    
    sources = []
    for line in script_text.strip().split('\n'):
        line = line.strip()
        # Case insensitive check for # FUENTES: or # SOURCES:
        if line.startswith('#') and any(k in line.upper() for k in ['FUENTES:', 'SOURCES:']):
            parts = line.split(':', 1)
            if len(parts) > 1:
                val = parts[1].strip()
                if val:
                    sources.append(val)
    
    return ", ".join(sources)

def validate_script_syntax(script_text, project):
    """
    Checks for errors in the script and calculates estimated duration.
    Supports both Legacy (columns) and AVGL (tags).
    Returns (is_valid, error_list, estimated_duration_seconds, total_scenes)
    """
    from django.conf import settings
    errors = []
    total_seconds = 0
    WORDS_PER_SECOND = 145 / 60.0
    
    # --- 1. Detect Format ---
    is_avgl = '<scene' in script_text.lower()
    
    if is_avgl:
        try:
            script_obj = parse_avgl_script(script_text)
            scenes = script_obj.get_all_scenes()
            if not scenes:
                errors.append("Se detectó formato AVGL pero no se encontraron bloques <scene> válidos.")
                return False, errors, 0, 0
            
            for scene in scenes:
                word_count = len(scene.clean_text.split())
                scene_duration = (word_count / WORDS_PER_SECOND)
                
                # Add pauses from events
                for event in scene.events:
                    if event.type == 'pause':
                        try: scene_duration += float(event.params.get('duration', 0))
                        except: pass
                
                total_seconds += scene_duration + 0.5 # Scene overhead
            
            return True, errors, total_seconds, len(scenes)
        except Exception as e:
            errors.append(f"Error parseando AVGL: {str(e)}")
            return False, errors, 0, 0
            
    # --- 2. Legacy Format (Existing logic) ---
    lines = script_text.strip().split('\n')
    # ... (existing legacy parsing logic)


def generate_video_process(project):
    from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, VideoFileClip, CompositeAudioClip, CompositeVideoClip, AudioClip, afx
    from moviepy.audio.AudioClip import concatenate_audioclips
    import time
    logger = ProjectLogger(project)
    logger.log(f"--- INICIO DE GENERACIÓN: {project.title} ---")
    
    # 1. PRE-RENDER VALIDATION & ESTIMATION
    is_valid, syntax_reports, est_duration, total_scenes = validate_script_syntax(project.script_text, project)
    
    # Log warnings/errors but don't stop if it's just missing files
    has_critical = any("Formato incorrecto" in e or "Etiqueta de pausa" in e for e in syntax_reports)
    
    if syntax_reports:
        report_msg = "📋 REPORTE DE GUION:\n" + "\n".join(syntax_reports)
        logger.log(report_msg)
        
    if has_critical:
        logger.log("🛑 DETENIDO: Errores críticos de formato detectados.")
        project.status = 'failed'
        project.save(update_fields=['status'])
        return

    m, s = divmod(int(est_duration), 60)
    logger.log(f"⏱️ Duración estimada del video: {m:02d}:{s:02d}")
    
    # IMPROVED ESTIMATION LOGIC (v2.21.4): Recalibrated based on actual performance
    # Previous: 17 min for 4min video. Now target: ~4-5 min.
    # 
    # Factors:
    # - Base: 12s per scene (TTS generation + setup)
    # - Render: 3.5x duration (H.264 encoding)
    # - Overlay penalty: +10s per scene (compositing)
    # - Effect penalty: +5s per scene (transfomations)
    
    base_per_scene = 12
    duration_factor = 3.5
    
    # Count overlays and effects from script
    overlay_count = 0
    effect_count = 0
    for line in project.script_text.strip().split('\n'):
        line = line.strip()
        if not line or '[PAUSA:' in line:
            continue
        if 'OVERLAY:' in line.upper():
            overlay_count += 1
        # Ken Burns or ZOOM effects
        if any(effect in line.upper() for effect in ['HOR:', 'VER:', 'ZOOM']):
            effect_count += 1
    
    est_proc_seconds = (
        (total_scenes * base_per_scene) +           # Base overhead
        int(est_duration * duration_factor) +       # Encoding time
        (overlay_count * 10) +                       # Overlay penalty
        (effect_count * 5)                          # Effect penalty
    )
    
    if est_proc_seconds < 60:
        logger.log(f"🖥️ Tiempo estimado de procesamiento: ~{est_proc_seconds} seg")
    else:
        logger.log(f"🖥️ Tiempo estimado de procesamiento: ~{int(est_proc_seconds / 60)} min")
    
    project.status = 'processing'
    project.save(update_fields=['status'])
    
    try:
        # Determine voice
        voice_to_use = project.voice_id
        edge_rate = os.getenv("EDGE_RATE", "+0%")
        if project.engine == 'edge':
            if not voice_to_use:
                voice_to_use = os.getenv("EDGE_VOICE", "es-DO-EmilioNeural")
        else:
            if not voice_to_use:
                voice_to_use = os.getenv("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")

        # Parse Script
        sections = []
        lines = [l.strip() for l in project.script_text.strip().split('\n') if l.strip()]
        total_scenes = len(lines)
        
        # 2. SHOW PREVIEW OF YOUTUBE DESCRIPTION (v2.21.2)
        try:
            from .utils import extract_hashtags_from_script
            script_tags = extract_hashtags_from_script(project.script_text)
            
            fixed_tags = os.getenv(
                'YOUTUBE_FIXED_HASHTAGS',
                '#IA #notiaci #ciencia #tecnologia #noticias #avances #avancesmedicos #carlosramirez #descubrimientos'
            ).strip()
            
            # Clean quotes
            if (fixed_tags.startswith('"') and fixed_tags.endswith('"')) or \
               (fixed_tags.startswith("'") and fixed_tags.endswith("'")):
                fixed_tags = fixed_tags[1:-1].strip()
            
            all_tags = (script_tags + " " + fixed_tags).strip()
            
            preview_msg = (
                "\n"
                "📝 PREVISUALIZACIÓN YOUTUBE:\n"
                f"🎬 Título: {project.title}\n"
                "🏷️ Tags sugeridos:\n"
                f"{all_tags}\n"
                "📍 (Los capítulos/timestamps se generarán dinámicamente)\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            )
            logger.log(preview_msg)
        except Exception as e:
            logger.log(f"⚠️ No se pudo generar la previsualización de YouTube: {e}")

        start_time_global = time.time()

        # 4. MAIN GENERATION LOOP
        is_avgl = '<scene' in project.script_text.lower()
        has_avgl_music = False
        clips = []
        voice_intervals = []
        current_time = 0
        timestamps_list = []
        
        # Pre-load settings
        temp_audio_dir = os.path.join(settings.MEDIA_ROOT, 'temp_audio')
        os.makedirs(temp_audio_dir, exist_ok=True)
        assets_dir = os.path.join(settings.MEDIA_ROOT, 'assets')
        available_images = []
        if os.path.exists(assets_dir):
            available_images = [os.path.join(assets_dir, f) for f in os.listdir(assets_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.mp4'))]

        TARGET_SIZE = (1080, 1920) if project.aspect_ratio == 'portrait' else (1920, 1080)

        if is_avgl:
            script_data = parse_avgl_script(project.script_text)
            
            # UNIFIED TITLE UPDATE (Regla de Oro v3.0 Plus)
            if script_data.title and script_data.title != "Video Sin Título":
                project.title = script_data.title
                project.save()
            
            # Flatten scenes for processing but keep block metadata
            all_scenes = []
            for block in script_data.blocks:
                all_scenes.extend(block.scenes)
            
            total_scenes = len(all_scenes)
            
            for i, scene in enumerate(all_scenes):
                # Priority: Scene-level <music> event > Block-level music > UI Selection
                scene_music_override = scene.music # Inherited from block
                
                # Check for in-scene music tag that might override block music
                for event in scene.events:
                    if event.type == 'music' and 'type' in event.params:
                        scene_music_override = event.params['type']
                    elif event.type == 'music' and event.params.get('state') == 'stop':
                        scene_music_override = None # Stop music
                
                if scene_music_override:
                    has_avgl_music = True
                
                # CANCELLATION CHECK
                project.refresh_from_db()
                if project.status == 'cancelled':
                    logger.log("🛑 Proceso abortado por el usuario.")
                    return 

                logger.log(f"🎬 [AVGL] Procesando Escena {i+1}/{total_scenes}: {scene.title}")
                
                # --- A. Audio Generation (Scene Level) ---
                # v3.0 Alpha: We search for the first <voice> tag to override scene voice
                voice_override = None
                for event in scene.events:
                    if event.type == 'voice' and 'name' in event.params:
                        voice_override = event.params['name']
                        break
                
                active_voice = voice_override or voice_to_use
                
                clean_text = re.sub(r'\[.*?\]', '', scene.clean_text).strip()
                audio_path = os.path.join(temp_audio_dir, f"{project.id}_scene_{i}.mp3")
                
                scene_audio = None
                if clean_text:
                    if project.engine == 'edge':
                        asyncio.run(generate_audio_edge(clean_text, audio_path, active_voice, edge_rate))
                    else:
                        api_key = os.getenv("ELEVENLABS_API_KEY")
                        asyncio.run(generate_audio_elevenlabs(clean_text, audio_path, active_voice, api_key))
                    
                    if os.path.exists(audio_path):
                        scene_audio = AudioFileClip(audio_path)
                
                if not scene_audio:
                    scene_audio = AudioClip(lambda t: [0,0], duration=1.0) # Fallback if text empty
                
                # --- B. Timing Calculation ---
                total_duration = scene_audio.duration
                words = clean_text.split()
                spw = total_duration / len(words) if words else 0
                
                # Calculate absolute start times
                asset_switches = []
                ambient_events = []
                global_overlay_switches = [] # Tracking <overlay /> tags
                
                for event in scene.events:
                    event.start_time = event.offset_words * spw
                    if event.type == 'asset':
                        asset_switches.append(event)
                    elif event.type == 'ambient':
                        ambient_events.append(event)
                    elif event.type == 'overlay':
                        global_overlay_switches.append(event)
                
                # --- C. Build Visual Segments ---
                active_global_overlay = None # Current persistence
                scene_clips = []
                
                # Combine all visual triggers: assets and global overlays
                visual_timeline = sorted(asset_switches + global_overlay_switches, key=lambda e: e.start_time)
                
                # Ensure we start with an asset
                if not visual_timeline or visual_timeline[0].type != 'asset':
                    # Fallback or use first event's asset if any
                    visual_timeline.insert(0, AVGLEvent('asset', {'type': 'placeholder.png'}, 0))
                
                current_asset_event = visual_timeline[0]
                
                for idx, event in enumerate(visual_timeline):
                    start_t = event.start_time
                    end_t = visual_timeline[idx+1].start_time if idx+1 < len(visual_timeline) else total_duration
                    dur = end_t - start_t
                    
                    if event.type == 'overlay':
                        active_global_overlay = event.params.get('type')
                        # If the event is an overlay change, we continue with the PREVIOUS asset
                        # (The asset doesn't change, just the layer above it)
                        pass 
                    else:
                        current_asset_event = event
                    
                    if dur <= 0.05: continue 
                    
                    # Process Asset Segment
                    img_name = current_asset_event.params.get('type', 'placeholder.png')
                    img_path = os.path.join(settings.MEDIA_ROOT, 'assets', img_name)
                    if not os.path.exists(img_path) and available_images:
                        img_path = random.choice(available_images)
                    
                    if os.path.exists(img_path):
                        # Use local overlay if present, otherwise use global persistence
                        effective_params = current_asset_event.params.copy()
                        if not effective_params.get('overlay') and active_global_overlay:
                            effective_params['overlay'] = active_global_overlay
                            
                        segment_clip = apply_ken_burns_effect(img_path, TARGET_SIZE, dur, effect=effective_params)
                        segment_clip = segment_clip.with_start(start_t)
                        scene_clips.append(segment_clip)

                # --- D. Finalize Scene with SFX, Ambient, and Inherited Music ---
                audio_layers = [scene_audio]
                
                def resolve_audio_path(name, folder):
                    """Smart resolution: checks target folder, then music/assets as fallback"""
                    if not name: return None
                    search_folders = [folder, 'music', 'assets']
                    for f in search_folders:
                        base_path = os.path.join(settings.MEDIA_ROOT, f, name)
                        if os.path.exists(base_path): return base_path
                        if os.path.exists(base_path + ".mp3"): return base_path + ".mp3"
                    return None

                # 1. SFX
                for event in scene.events:
                    if event.type == 'sfx':
                        sfx_name = event.params.get('type')
                        sfx_path = resolve_audio_path(sfx_name, 'sfx')
                        if sfx_path:
                            try:
                                s_vol = float(event.params.get('volume', 0.5))
                                s_clip = AudioFileClip(sfx_path).with_effects([afx.MultiplyVolume(s_vol)]).with_start(event.start_time)
                                audio_layers.append(s_clip)
                            except Exception as e:
                                logger.log(f"   ⚠️ SFX corrupto o inválido ({sfx_name}): {e}")

                # 2. Ambient
                for env in ambient_events:
                    if env.params.get('state') == 'start':
                        env_type = env.params.get('type')
                        env_path = resolve_audio_path(env_type, 'ambient')
                        if env_path:
                            try:
                                env_audio = AudioFileClip(env_path)
                                env_vol = float(env.params.get('volume', 0.1))
                                loops = int(total_duration / env_audio.duration) + 1
                                env_looped = env_audio.with_effects([afx.AudioLoop(n_loops=loops)]).with_duration(total_duration - env.start_time)
                                env_looped = env_looped.with_effects([afx.MultiplyVolume(env_vol)]).with_start(env.start_time)
                                audio_layers.append(env_looped)
                            except Exception as e:
                                logger.log(f"   ⚠️ Ambiente corrupto o inválido ({env_type}): {e}")

                # 3. Inherited or Specific Music (PRIORITY MIX)
                # First, check for explicit tags in scene
                scene_explicit_music = []
                for event in scene.events:
                    if event.type == 'music' and event.params.get('state') != 'stop':
                        m_type = event.params.get('type')
                        m_path = resolve_audio_path(m_type, 'music')
                        if m_path:
                            try:
                                m_vol = float(event.params.get('volume', 0.2))
                                m_audio = AudioFileClip(m_path)
                                m_loops = int(total_duration / m_audio.duration) + 1
                                m_final = m_audio.with_effects([afx.AudioLoop(n_loops=m_loops)]).with_duration(total_duration - event.start_time)
                                m_final = m_final.with_effects([afx.MultiplyVolume(m_vol)]).with_start(event.start_time)
                                scene_explicit_music.append(m_final)
                            except Exception as e:
                                logger.log(f"   ⚠️ Música corrupta o inválida ({m_type}): {e}")
                
                # If no explicit music tags, use the inherited block music
                if not scene_explicit_music and scene_music_override:
                    m_path = resolve_audio_path(scene_music_override, 'music')
                    if m_path:
                        try:
                            m_vol = project.music_volume # Global UI volume as default for block music
                            m_audio = AudioFileClip(m_path)
                            m_loops = int(total_duration / m_audio.duration) + 1
                            m_final = m_audio.with_effects([afx.AudioLoop(n_loops=m_loops)]).with_duration(total_duration)
                            m_final = m_final.with_effects([afx.MultiplyVolume(m_vol)]).with_start(0)
                            audio_layers.append(m_final)
                        except Exception as e:
                            logger.log(f"   ⚠️ Música heredada corrupta ({scene_music_override}): {e}")
                else:
                    audio_layers.extend(scene_explicit_music)

                scene_audio_final = CompositeAudioClip(audio_layers)

                if scene_clips:
                    final_scene_video = CompositeVideoClip(scene_clips, size=TARGET_SIZE).with_audio(scene_audio_final)
                    mins, secs = divmod(int(current_time), 60)
                    timestamps_list.append(f"{mins:02d}:{secs:02d} - {scene.title}")
                    
                    clips.append(final_scene_video)
                    # Track voice intervals for ducking (AVGL treats whole scene as voice for now)
                    voice_intervals.append((current_time, current_time + total_duration))
                    current_time += total_duration
                
            # END OF AVGL LOOP
            
        else:
            # LEGACY GENERATION LOOP (v2.x)
            lines = [l.strip() for l in project.script_text.strip().split('\n') if l.strip()]
            for i, line in enumerate(lines):
                # CANCELLATION CHECK
                project.refresh_from_db()
                if project.status == 'cancelled':
                    logger.log("🛑 Proceso abortado por el usuario.")
                    return 

                # SKIP COMMENTS & TABLE DIVIDERS
                line_clean = line.strip()
                if line_clean.startswith('#') or not line_clean:
                    continue
                
                parts = [p.strip() for p in line_clean.split('|')]
                if len(parts) < 3: continue
                if parts[1].startswith('---'): continue

                image_name = parts[1]
                direction = parts[2] if len(parts) >= 3 else None
                text = ""
                pause_duration = 0
                
                if len(parts) >= 5:
                    text = parts[3]
                    try: pause_duration = float(parts[4]) if parts[4] else 0
                    except: pause_duration = 0
                elif len(parts) >= 4:
                    text = parts[3]
                else:
                    text = parts[2] # 3 column fallback

                logger.log(f"🎬 Procesando Escena {i+1}/{total_scenes}: {image_name}")
                
                # --- Audio Integration ---
                clean_text = re.sub(r'\[.*?\]', '', text).strip()
                audio_path = os.path.join(temp_audio_dir, f"{project.id}_audio_{i}.mp3")
                
                audio_clip = voice_clip = silence_clip = None
                
                if clean_text:
                    if project.engine == 'edge':
                        asyncio.run(generate_audio_edge(clean_text, audio_path, voice_to_use, edge_rate))
                    else:
                        api_key = os.getenv("ELEVENLABS_API_KEY")
                        asyncio.run(generate_audio_elevenlabs(clean_text, audio_path, voice_to_use, api_key))
                    
                    if os.path.exists(audio_path):
                        try:
                            voice_clip = AudioFileClip(audio_path)
                            voice_intervals.append((current_time, current_time + voice_clip.duration))
                        except Exception as e:
                            logger.log(f"   ⚠️ Audio de voz corrupto: {e}")
                
                if pause_duration > 0:
                    silence_clip = AudioClip(lambda t: [0, 0], duration=pause_duration)
                
                if voice_clip and silence_clip:
                    audio_clip = concatenate_audioclips([voice_clip, silence_clip])
                else:
                    audio_clip = voice_clip or silence_clip

                if not audio_clip: continue

                duration = audio_clip.duration + (0.5 if voice_clip else 0)
                
                # --- Visual Integration ---
                img_path = os.path.join(settings.MEDIA_ROOT, 'assets', image_name)
                if not os.path.exists(img_path) and available_images:
                    img_path = random.choice(available_images)
                if not os.path.exists(img_path): continue

                # --- Visual Clip Creation ---
                try:
                    is_video = img_path.lower().endswith(('.mp4', '.mov', '.avi', '.webm'))
                    if is_video:
                        video_clip = VideoFileClip(img_path).resized(TARGET_SIZE)
                        if video_clip.duration < duration:
                            loops = int(duration / video_clip.duration) + 1
                            video_clip = concatenate_videoclips([video_clip] * loops, method="chain")
                        final_clip = video_clip.subclipped(0, duration).with_audio(audio_clip)
                    else:
                        if direction:
                            final_clip = apply_ken_burns_effect(img_path, TARGET_SIZE, duration, effect=direction).with_audio(audio_clip)
                        else:
                            final_clip = ImageClip(img_path).resized(TARGET_SIZE).with_duration(duration).with_audio(audio_clip)

                    # --- Cinematographic Overlays (Legacy) ---
                    if direction and 'OVERLAY:' in direction.upper():
                        try:
                            ov_part = [p for p in direction.split('+') if 'OVERLAY:' in p.upper()][0]
                            overlay_file = ov_part.split(':')[1].strip()
                            if not overlay_file.lower().endswith('.mp4'): overlay_file += '.mp4'
                            overlay_path = os.path.join(settings.MEDIA_ROOT, 'overlays', overlay_file)
                            if os.path.exists(overlay_path):
                                ov_clip = VideoFileClip(overlay_path).resized(TARGET_SIZE)
                                ov_instance = ov_clip
                                if ov_instance.duration < duration:
                                    ov_loops = int(duration / ov_instance.duration) + 1
                                    ov_instance = concatenate_videoclips([ov_instance] * ov_loops, method="chain")
                                ov_instance = ov_instance.subclipped(0, duration)
                                
                                ov_vol = 0
                                ov_parts = ov_part.split(':')
                                if len(ov_parts) >= 3:
                                    try: ov_vol = float(ov_parts[2])
                                    except: ov_vol = 0
                                
                                if ov_vol > 0: ov_instance = ov_instance.with_effects([afx.MultiplyVolume(ov_vol / 10.0)])
                                else: ov_instance = ov_instance.without_audio()
                                
                                ov_instance = ov_instance.with_mask(ov_instance.to_mask()).with_opacity(0.4)
                                final_clip = CompositeVideoClip([final_clip, ov_instance], size=TARGET_SIZE).with_duration(duration)
                        except: pass

                    mins, secs = divmod(int(current_time), 60)
                    timestamps_list.append(f"{mins:02d}:{secs:02d} - {scene.title}")
                    
                    clips.append(final_clip)
                    current_time += duration
                except Exception as e:
                    logger.log(f"   ⚠️ Escena {i+1}: Error visual ({e}).")
        
        if clips:
            logger.log("Concatenating clips with optimized method...")
            # Use method="chain" which is MUCH faster than "compose"
            final_video = concatenate_videoclips(clips, method="chain")
            
            # --- Background Music Integration with Ducking ---
            if project.background_music and not has_avgl_music:
                try:
                    logger.log(f"Adding background music with Ducking: {project.background_music.name}")
                    bg_music_path = project.background_music.file.path
                    if os.path.exists(bg_music_path):
                        bg_audio = AudioFileClip(bg_music_path)
                        
                        # Loop music
                        loops = int(final_video.duration / bg_audio.duration) + 1
                        bg_audio_looped = bg_audio.with_effects([afx.AudioLoop(n_loops=loops)]).with_duration(final_video.duration)
                        
                        # DUCKING LOGIC
                        # music_volume is the peak level (no voice)
                        peak_vol = project.music_volume
                        duck_vol = peak_vol * 0.15 # Ducking to 15% of user preference
                        
                        fade_t = 0.2 # Duration of volume transition

                        def volume_ducking(t):
                            if isinstance(t, np.ndarray):
                                # Optimized vector processing for arrays
                                vol = np.full(t.shape, peak_vol)
                                for start, end in voice_intervals:
                                    # Ducking core
                                    vol[(t >= start) & (t <= end)] = duck_vol
                                    
                                    # Fade-out (Peak to Duck)
                                    mask_fade_out = (t >= (start - fade_t)) & (t < start)
                                    if np.any(mask_fade_out):
                                        # Simple linear interpolation: from peak to duck
                                        progress = (t[mask_fade_out] - (start - fade_t)) / fade_t
                                        vol[mask_fade_out] = peak_vol - (progress * (peak_vol - duck_vol))
                                    
                                    # Fade-in (Duck to Peak)
                                    mask_fade_in = (t > end) & (t <= (end + fade_t))
                                    if np.any(mask_fade_in):
                                        # Simple linear interpolation: from duck to peak
                                        progress = (t[mask_fade_in] - end) / fade_t
                                        vol[mask_fade_in] = duck_vol + (progress * (peak_vol - duck_vol))
                                return vol.reshape(-1, 1)
                            else:
                                # Standard scalar processing
                                for start, end in voice_intervals:
                                    if start <= t <= end:
                                        return duck_vol
                                    if (start - fade_t) <= t < start:
                                        progress = (t - (start - fade_t)) / fade_t
                                        return peak_vol - (progress * (peak_vol - duck_vol))
                                    if end < t <= (end + fade_t):
                                        progress = (t - end) / fade_t
                                        return duck_vol + (progress * (peak_vol - duck_vol))
                                return peak_vol

                        # Apply dynamic volume transformation
                        bg_audio_final = bg_audio_looped.transform(lambda get_f, t: get_f(t) * volume_ducking(t))
                        
                        # Mix tracks
                        final_audio = CompositeAudioClip([final_video.audio, bg_audio_final])
                        final_video = final_video.with_audio(final_audio)
                except Exception as music_err:
                    logger.log(f"Warning: Failed to add background music: {music_err}")
            # ------------------------------------
            
            safe_title = slugify(project.title) or f"video_{project.id}"
            output_filename = f"{safe_title}.mp4"
            output_rel_path = f"videos/{output_filename}"
            output_full_path = os.path.join(settings.MEDIA_ROOT, 'videos', output_filename)
            os.makedirs(os.path.dirname(output_full_path), exist_ok=True)
            
            # 8. WRITE FINAL VIDEO (v2.21.x - Standard libx264)
            logger.log("Writing final video file...")
            import multiprocessing
            n_threads = multiprocessing.cpu_count()
            
            render_start = time.time()
            final_video.write_videofile(
                output_full_path, 
                fps=24, 
                logger=None, 
                threads=n_threads,
                preset="superfast",
                codec="libx264",
                audio_codec="aac"
            )
            render_end = time.time()
            logger.log(f"📊 Tiempo de renderizado final: {int(render_end - render_start)} seg.")
            
            # Thumbnail
            try:
                thumb_filename = f"{safe_title}_thumb.png"
                thumb_rel_path = f"thumbnails/{thumb_filename}"
                thumb_full_path = os.path.join(settings.MEDIA_ROOT, 'thumbnails', thumb_filename)
                os.makedirs(os.path.dirname(thumb_full_path), exist_ok=True)
                final_video.save_frame(thumb_full_path, t=1.0)
                project.thumbnail.name = thumb_rel_path
            except:
                pass # processing err
            
            project.output_video.name = output_rel_path
            project.status = 'completed'
            project.timestamps = "\n".join(timestamps_list)  # Save YouTube chapters
            
            # v2.24.3 - Persist project data BEFORE auto-upload to avoid 'refresh_from_db' cleaning memory
            project.save(update_fields=['status', 'output_video', 'thumbnail', 'timestamps', 'script_hashtags', 'log_output'])
            
            end_time_global = time.time()
            total_elapsed = end_time_global - start_time_global
            em, es = divmod(int(total_elapsed), 60)
            
            logger.log(f"✅ ¡Video generado con éxito en {em:02d}:{es:02d}!")

            # 9. AUTO-UPLOAD TO YOUTUBE (v2.24.0)
            if project.auto_upload_youtube:
                logger.log("[YouTube] 🚀 Iniciando subida automática...")
                try:
                    from .youtube_utils import get_youtube_client, generate_youtube_description, upload_video
                    youtube = get_youtube_client()
                    if youtube:
                        # Refresh project to get final timestamps/hashtags (if updated concurrently)
                        project.refresh_from_db() 
                        description = generate_youtube_description(project)
                        
                        result = upload_video(youtube, project.output_video.path, project.title, description)
                        
                        if result and 'id' in result:
                            project.youtube_video_id = result['id']
                            video_url = f"https://www.youtube.com/watch?v={result['id']}"
                            logger.log(f"[YouTube] ✅ Subida automática exitosa: {video_url}")
                        else:
                            logger.log("[YouTube] ⚠️ Subida completada pero no se recibió confirmación.")
                    else:
                        logger.log("[YouTube] ❌ Error: No se encontró token de autorización. Debes autorizar YouTube manualmente primero.")
                except Exception as ex:
                    logger.log(f"[YouTube] ❌ Error en subida automática: {str(ex)}")

        else:
            project.status = 'failed'
            logger.log("No clips were generated.")

    except Exception as e:
        logger.log(f"Critical Error: {str(e)}")
        import traceback
        logger.log(traceback.format_exc())
        project.status = 'failed'
    
    # Selective save to protect Title from accidental mutations
    project.save(update_fields=['status', 'output_video', 'thumbnail', 'timestamps', 'script_hashtags', 'log_output', 'youtube_video_id'])
