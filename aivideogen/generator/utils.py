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
import time
import whisper
import subprocess
import re
import shutil

# v5.14: Global FFmpeg Robust Initialization
# Ensure FFmpeg is available for Whisper and other subprocesses globally
try:
    import imageio_ffmpeg
    ffmpeg_original = imageio_ffmpeg.get_ffmpeg_exe()
    # Use a localized bin dir for the project
    local_bin = os.path.join(os.getcwd(), 'aivideogen', 'media', 'bin')
    os.makedirs(local_bin, exist_ok=True)
    
    ffmpeg_target = os.path.join(local_bin, "ffmpeg.exe")
    if not os.path.exists(ffmpeg_target):
        try:
            shutil.copy2(ffmpeg_original, ffmpeg_target)
        except:
            pass
            
    if local_bin not in os.environ["PATH"]:
        os.environ["PATH"] = local_bin + os.pathsep + os.environ["PATH"]
except Exception as e:
    pass

# Global model instance to avoid re-loading for every scene
_WHISPER_MODEL = None
def get_whisper_model():
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"[HW] Cargando Whisper en dispositivo: {device.upper()}")
            _WHISPER_MODEL = whisper.load_model("small", device=device)
        except Exception as e:
            print(f"[-] Error cargando Whisper global: {e}")
            try:
                _WHISPER_MODEL = whisper.load_model("small")
            except:
                pass
    return _WHISPER_MODEL

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
- Inicio (0-2s): Empieza SIEMPRE con: "Bienvenidos a mi canal. Según informes de {news_item.source.name}, [DATO IMPACTANTE DIRECTO SIN RELLENO]".
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

def translate_script_ai(script_data, target_lang="es"):
    """
    Translates an AVGL script JSON into the target language using Gemini.
    Translates 'text' and 'subtitle' fields of each scene.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None, "Error: No se encontró GEMINI_API_KEY."

    lang_name = "Español" if target_lang == "es" else "Inglés"
    
    prompt = f"""
    Eres un traductor experto en doblaje cinematográfico y discursos políticos.
    Tu tarea es traducir el siguiente guion de video al {lang_name}.
    
    REGLAS:
    1. Mantén la estructura de bloques y escenas exacta.
    2. Traduce ÚNICAMENTE los campos "text" y "subtitle" de cada escena.
    3. NO modifiques nombres de archivos, IDs, tiempos ni configuraciones.
    4. El tono debe ser épico, profesional y adaptado al contexto político.
    5. Devuelve ÚNICAMENTE el JSON resultante.
    
    GUION A TRADUCIR:
    {json.dumps(script_data, ensure_ascii=False)}
    """

    model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-flash-latest")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"response_mime_type": "application/json"}
    }

    try:
        response = requests.post(url, json=payload, timeout=60)
        if response.status_code == 200:
            result = response.json()
            content = result['candidates'][0]['content']['parts'][0]['text']
            return json.loads(content), None
        else:
            return None, f"Error Gemini: {response.status_code}"
    except Exception as e:
        return None, str(e)

def translate_text_ai(text, target_lang="es"):
    """
    Translates a single string into the target language using Gemini.
    """
    if not text or not text.strip():
        return text, None
        
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return text, "Error: No se encontró GEMINI_API_KEY."

    langs = {
        'es': 'Español', 'en': 'Inglés', 'fr': 'Francés', 'it': 'Italiano', 
        'pt': 'Portugués', 'de': 'Alemán', 'ja': 'Japonés', 'zh': 'Chino'
    }
    lang_name = langs.get(target_lang.lower(), "Español")
    
    prompt = f"""
    Eres un traductor experto en doblaje y localización cinematográfica.
    Tu misión es traducir el siguiente texto de entrada al {lang_name}.
    
    INSTRUCCIONES CRÍTICAS:
    1. El resultado debe estar ÚNICAMENTE en {lang_name}. NO incluyas notas ni el texto original.
    2. Mantén el estilo, la emoción y las pausas del locutor original.
    3. Responde exclusivamente en formato JSON con la clave "translated_text".
    
    TEXTO A TRADUCIR:
    {text}
    """

    model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-flash-latest")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"response_mime_type": "application/json"}
    }

    MAX_RETRIES = 3
    for attempt in range(MAX_RETRIES):
        try:
            import requests, json
            response = requests.post(url, json=payload, timeout=120)
            if response.status_code == 200:
                result = response.json()
                raw_content = result['candidates'][0]['content']['parts'][0]['text']
                
                # Parse JSON for safety
                try:
                    data = json.loads(raw_content)
                    translated = data.get("translated_text", "").strip()
                except:
                    # Fallback to legacy string clean if JSON fails
                    translated = raw_content.replace("```json", "").replace("```", "").strip()
                
                if not translated:
                     return text, "Gemini devolvió una traducción vacía."
                return translated, None
            elif response.status_code == 429:
                if attempt < MAX_RETRIES - 1:
                    # Exponential backoff
                    wait_time = (attempt + 1) * 10 
                    time.sleep(wait_time)
                    continue
                return text, f"Error Gemini (Rate Limit): 429 tras {MAX_RETRIES} intentos"
            else:
                return text, f"Error Gemini: {response.status_code}"
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(5)
                continue
            return text, f"Error de conexión Gemini: {str(e)}"

def auto_transcribe_and_translate_asset(video_path, target_lang="es", logger=None, start_time=0.0, duration=None):
    """
    v5.3: Autonomous Dubbing Chain with temporal clipping.
    """
    if not os.path.exists(video_path):
        return None, f"Archivo no encontrado: {video_path}"

    try:
        # 1. FFmpeg setup (v5.13: Robust Injection)
        import imageio_ffmpeg, shutil
        ffmpeg_original = imageio_ffmpeg.get_ffmpeg_exe()
        bin_dir = os.path.join(settings.MEDIA_ROOT, 'bin')
        os.makedirs(bin_dir, exist_ok=True)
        
        ffmpeg_target = os.path.join(bin_dir, "ffmpeg.exe")
        if not os.path.exists(ffmpeg_target):
            try:
                shutil.copy2(ffmpeg_original, ffmpeg_target)
            except Exception as e:
                # Fallback to dir injection if copy fails
                bin_dir = os.path.dirname(ffmpeg_original)
        
        # Priority PATH injection
        if bin_dir not in os.environ["PATH"]:
            os.environ["PATH"] = bin_dir + os.pathsep + os.environ["PATH"]

        import time
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_audio')
        os.makedirs(temp_dir, exist_ok=True)
        temp_audio = os.path.join(temp_dir, f"dub_temp_{int(time.time())}_{os.getpid()}.wav")
        
        if logger: logger.log(f"      [Dubbing] Extrayendo segmento ({start_time}s, {duration}s) para transcripción...")
        
        # v5.19: Reference Fix
        ffmpeg_bin = ffmpeg_target if os.path.exists(ffmpeg_target) else ffmpeg_original
        
        # v5.3: Optimized command
        cmd = [
            ffmpeg_bin, "-y", 
            "-ss", str(start_time),
            "-i", video_path
        ]
        if duration:
            cmd.extend(["-t", str(duration)])
            
        cmd.extend([
            "-af", "volume=2.5,highpass=f=100,lowpass=f=8000",
            "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
            temp_audio
        ])
        subprocess.run(cmd, check=True, capture_output=True)

        # 2. Transcription
        if logger: logger.log(f"      [Dubbing] Iniciando Whisper (Modelo: small)...")
        model = get_whisper_model()
        if not model:
            return None, "No se pudo cargar el modelo Whisper."
            
        # Ensure audio path is absolute for Windows stability
        temp_audio_abs = os.path.abspath(temp_audio)
        if not os.path.exists(temp_audio_abs):
             return None, f"Archivo temporal de audio no encontrado: {temp_audio_abs}"
             
        result = model.transcribe(temp_audio_abs)
        original_text = result.get("text", "").strip()
        
        # Cleanup temp audio
        if os.path.exists(temp_audio): os.remove(temp_audio)

        if not original_text:
            return None, "No se detectó habla en el video."

        if logger: logger.log(f"      [Dubbing] Transcripción exitosa: {original_text[:50]}...")

        # 3. Translation
        if logger: logger.log(f"      [Dubbing] Traduciendo al {target_lang}...")
        translated, err = translate_text_ai(original_text, target_lang)
        
        if err:
            if logger: logger.log(f"        ⚠️ Transcrito pero no traducido: {err}. Usando texto original como fallback.")
            return original_text, None # Retornamos éxito con el texto original
            
        return translated, None

    except Exception as e:
        return None, f"Error en Auto-Dubbing: {str(e)}"

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
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamped_message = f"[{now}] {message}"
        
        try:
            print(f"[Project {self.project.id}] {timestamped_message}", flush=True)
        except UnicodeEncodeError:
            clean_msg = timestamped_message.encode('ascii', 'ignore').decode('ascii')
            print(f"[Project {self.project.id}] {clean_msg}", flush=True)

        self.log_buffer.append(timestamped_message)
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
    
    # Init Logger for start message
    logger = ProjectLogger(project)
    logger.log(f"Using Unified AVGL v4.0 Engine (Single Pipeline)")
    
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
            logger = ProjectLogger(project)
            logger.log(f"[YouTube] [ERROR] Error fatal disparando subida automatica: {e}")

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
