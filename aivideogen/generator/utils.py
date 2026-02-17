import requests
import os
import random
import asyncio
import json
from django.conf import settings
# from moviepy import ImageClip, AudioFileClip, ... (Moved to function level)
# import edge_tts (Moved to function level)
# from elevenlabs.client import ElevenLabs (Moved to function level)
# from elevenlabs import save (Moved to function level)
from django.utils.text import slugify

def generate_script_ai(news_item):
    """
    Generates a high-impact script and visual prompts for a news item using Gemini API.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None, "Error: No se encontró GEMINI_API_KEY en las variables de entorno.", None, None

    prompt = f"""
Eres un guionista experto en YouTube Shorts de tecnología y ciencias para el canal "Noticias de IA y ciencias".
Tu objetivo es transformar la noticia adjunta en un guion de alto impacto de máximo 2 minutos y medio.

REGLAS CRÍTICAS DE FORMATO:
1. El guion debe estar compuesto por líneas con el formato exacto: TITULO | nombre_archivo.png | Texto a locutar
2. El separador debe ser " | " (tubo con espacios).
3. NO uses tablas de Markdown, ni negritas (**), ni corchetes [], ni llaves {{}} en el texto.
4. Las imágenes deben tener nombres descriptivos como 'robot_ia.png' o 'laboratorio_ciencia.mp4'.

ESTRATEGIA DE CONTENIDO (HOOK-FIRST):
- Inicio (0-2s): Empieza SIEMPRE con: "Bienvenidos a Noticias de IA y ciencias. Según informes de {news_item.source.name}, [DATO IMPACTANTE DIRECTO SIN RELLENO]".
  Nota: Usa siempre "Inicio" como título de la primera escena, NUNCA uses "Gancho".
- Ritmo: Cambia de imagen/escena cada 2-4 segundos (aproximadamente cada 8-12 palabras).
- Conclusión Profunda: Incluye al menos una línea con "CONCLUSIÓN PROFUNDA" en el texto.
- Cierre: Termina con una pregunta provocadora para comentarios y pide suscripción.

DATOS DE LA NOTICIA:
Título: {news_item.title}
Resumen: {news_item.summary}
Fuente: {news_item.source.name}

RESPUESTA REQUERIDA (Formato JSON): Debes responder con un objeto JSON que tenga los siguientes campos:
1. "script": El guion completo siguiendo el formato TITULO | imagen.png | Texto
2. "prompts": Una lista de objetos con "file" y "prompt".
3. "music_suggestion": Breve descripción del estilo musical.
4. "hashtags": Una lista de 10-12 hashtags sugeridos (mix de marca, tema y contenido).

Responde ÚNICAMENTE el JSON.
"""

    model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-flash-latest")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "response_mime_type": "application/json"
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            content = result['candidates'][0]['content']['parts'][0]['text']
            import json
            data = json.loads(content)
            
            # Extract hashtags
            hashtags_list = data.get('hashtags', [])
            hashtags_str = " ".join(hashtags_list) if hashtags_list else ""
            
            return data.get('script'), data.get('prompts'), data.get('music_suggestion'), hashtags_str
        else:
            return None, f"Error de API Gemini: {response.status_code} - {response.text}", None, None
    except Exception as e:
        return None, f"Error durante la generación con IA: {str(e)}", None, None

def extract_sources_from_script(script_text):
    """
    Extracts source information from the script text.
    v8.0: Supports JSON format by looking for "fuentes" or "sources" keys.
    """
    if not script_text:
        return ""
    
    script_text = script_text.strip()
    
    # 1. Try JSON Extraction
    if script_text.startswith('{') and script_text.endswith('}'):
        try:
            import json
            data = json.loads(script_text)
            sources = data.get('fuentes') or data.get('sources') or data.get('fuente') or data.get('source')
            if sources:
                return str(sources).strip()
        except:
            pass

    # 2. Try REGEX Extraction (Legacy Text Format)
    import re
    # Look for "Fuente: X" or "Source: X"
    # Capture the rest of the line
    match = re.search(r'(?:Fuente|Source|Basado en|Fuentes):\s*(.*)', script_text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
        
    return ""

def extract_hashtags_from_script(script_text):
    """
    Extracts hashtags from the script text.
    v8.0: Supports JSON format by looking for "hashtags" key.
    """
    if not script_text:
        return ""
        
    script_text = script_text.strip()
    
    # 1. Try JSON list
    if script_text.startswith('{') and script_text.endswith('}'):
        try:
            import json
            data = json.loads(script_text)
            tags = data.get('hashtags')
            if isinstance(tags, list):
                return " ".join([f"#{t.strip().replace('#', '')}" for t in tags if t.strip()])
            elif isinstance(tags, str):
                return tags.strip()
        except:
            pass

    # 2. Try REGEX Extraction (Universal)
    import re
    # Find all words starting with #
    hashtags = re.findall(r'#\w+', script_text)
    
    # Return as space-separated string unique tags
    unique_tags = list(set(hashtags))
    return " ".join(unique_tags)

def get_human_title(raw_title):
    """
    Cleans technical filenames into human-readable titles.
    Example: "mechazilla_short.json" -> "Mechazilla Short"
    """
    import os
    if not raw_title:
        return "Video Sin Titulo"
    
    # Remove extension
    name, _ = os.path.splitext(raw_title)
    
    # Replace underscores and hyphens with spaces
    clean_name = name.replace('_', ' ').replace('-', ' ')
    
    # Capitalize words
    return clean_name.strip().title()

def generate_contextual_tags(project):
    """
    Intelligently generates contextual tags based on title and script content.
    Returns a list of unique tags (without #).
    """
    import re
    tags = []
    
    human_title = get_human_title(project.title)
    
    # 1. From Human Title
    if human_title:
        # Remove common stop words and punctuation
        clean_title = re.sub(r'[^\w\s]', '', human_title)
        # Add significant words (>3 chars)
        tags.extend([w.lower() for w in clean_title.split() if len(w) > 3])
    
    # 1. From Human Title (Sanitized)
    if human_title:
        # Remove common stop words and punctuation
        clean_title = re.sub(r'[^\w\s]', '', human_title)
        # Add significant words (>3 chars)
        tags.extend([w.lower() for w in clean_title.split() if len(w) > 3])

    # 2. From Script Keywords (Neuralink, SpaceX, etc.)
    # Look for known high-impact entities in the script
    entities = [
        'Neuralink', 'SpaceX', 'Starship', 'Musk', 'AGI', 'IA', 'AI', 
        'NASA', 'Artemis', 'Robot', 'Humanoid', 'Cancer', 'Salud',
        'Elon', 'Mars', 'Marte', 'Luna', 'Moon', 'Tesla'
    ]
    
    script_lower = project.script_text.lower()
    for entity in entities:
        if entity.lower() in script_lower:
            tags.append(entity.lower())

    # 3. Deduplicate and clean
    # Remove common irrelevant words if title extraction was too broad
    stop_words = {'video', 'resumen', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre', '2026', '2025'}
    final_tags = [t for t in dict.fromkeys(tags) if t not in stop_words]
    
    return final_tags

class ProjectLogger:
    def __init__(self, project):
        self.project = project
        self.log_buffer = []

    def log(self, message):
        # Remove emojis for console compatibility if they cause issues
        # But we mostly rely on the wrapped sys.stdout now.
        try:
            print(f"[Project {self.project.id}] {message}", flush=True)
        except UnicodeEncodeError:
            # Fallback for very old/strict consoles
            clean_msg = message.encode('ascii', 'ignore').decode('ascii')
            print(f"[Project {self.project.id}] {clean_msg}", flush=True)

        self.log_buffer.append(message)
        self.project.log_output = "\n".join(self.log_buffer)
        self.project.save(update_fields=['log_output'])

async def generate_audio_edge(text, output_path, voice="es-ES-AlvaroNeural", rate=None):
    import edge_tts
    if not rate:
        rate = os.getenv("EDGE_TTS_RATE", "+0%")
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output_path)


def generate_video_process(project):
    """
    Smart router (Unified v3.0):
    - All requests (JSON or Text) are routed to AVGL v4 engine.
    - Legacy engine has been removed. Text conversion happens inside parse_avgl_json.
    """
    import json
    from .video_engine import generate_video_avgl
    
    # Remove markdown code blocks if present (common copy-paste error)
    script_text = project.script_text.strip()
    if script_text.startswith('```'):
        # Remove first line (```json or ```)
        parts = script_text.split('\n', 1)
        if len(parts) > 1:
            script_text = parts[1]
            
        # Remove last line if it is ```
        if script_text.strip().endswith('```'):
            script_text = script_text.rsplit('```', 1)[0]
    
    # Update model (in memory) to use clean script
    project.script_text = script_text.strip()
    
    print(f"[Project {project.id}] Using Unified AVGL v4.0 Engine (Single Pipeline)")
    
    # Call the Unified Engine
    # Note: parse_avgl_json inside this function handles JSON vs Text conversion
    try:
        generate_video_avgl(project)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger = ProjectLogger(project)
        logger.log(f"[ERROR] Error CRITICO en Motor V15.7: {e}\n{tb}")
        project.status = 'error'
        project.save()

    # ═══════════════════════════════════════════════════════════════════
    # POST-PROCESSING: Automatic YouTube Upload
    # ═══════════════════════════════════════════════════════════════════
    # Refresh project to get latest status if it was modified elsewhere
    project.refresh_from_db()

    if project.status == 'completed' and project.auto_upload_youtube:
        try:
            from .youtube_utils import trigger_auto_upload
            trigger_auto_upload(project)
        except Exception as e:
            print(f"[YouTube] Error fatal disparando subida automatica: {e}")
            project.log_output += f"\n[YouTube] [ERROR] Error fatal disparando subida automatica: {e}"
            project.save(update_fields=['log_output'])

def cleanup_garbage(base_dir=None):
    """
    Agresively cleans up temporary files left by MoviePy and TTS engines.
    """
    import glob
    import os
    
    if not base_dir:
        base_dir = settings.BASE_DIR
        
    print(f"🧹 [Garbage Collector] Iniciando limpieza en {base_dir}...")
    
    # 1. Clean MoviePy Temp Files (*TEMP_MPY*)
    # These are often locked until the process closes, but we try anyway.
    temp_mpy_files = glob.glob(os.path.join(base_dir, "*TEMP_MPY*"))
    for f in temp_mpy_files:
        try:
            os.remove(f)
            print(f"   🗑️ Eliminado: {os.path.basename(f)}")
        except Exception as e:
            print(f"   ⚠️ No se pudo borrar {os.path.basename(f)}: {e}")

    # 2. Clean Temp Audio Folder
    # We clear the entire folder to ensure no residue is left.
    temp_audio_dir = os.path.join(base_dir, 'aivideogen', 'media', 'temp_audio')
    if os.path.exists(temp_audio_dir):
        for f in os.listdir(temp_audio_dir):
            if f == ".gitkeep": continue
            file_path = os.path.join(temp_audio_dir, f)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                pass
    
    print("✨ [Garbage Collector] Limpieza finalizada.")
