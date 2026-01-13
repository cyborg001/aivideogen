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
        return None, "Error: No se encontró GEMINI_API_KEY en las variables de entorno.", None

    prompt = f"""
Eres un guionista experto en YouTube Shorts de tecnología y ciencias para el canal "Noticias de IA y ciencias".
Tu objetivo es transformar la noticia adjunta en un guion de alto impacto de máximo 2 minutos y medio.

REGLAS CRÍTICAS DE FORMATO:
1. El guion debe estar compuesto por líneas con el formato exacto: TITULO | nombre_archivo.png | Texto a locutar
2. El separador debe ser " | " (tubo con espacios).
3. NO uses tablas de Markdown, ni negritas (**), ni corchetes [], ni llaves {{}} en el texto.
4. Las imágenes deben tener nombres descriptivos como 'robot_ia.png' o 'laboratorio_ciencia.mp4'.

ESTRATEGIA DE CONTENIDO (HOOK-FIRST):
- Comienzo (0-2s): Empieza SIEMPRE con: "Bienvenidos a Noticias de IA y ciencias. Según informes de {news_item.source.name}, [DATO IMPACTANTE DIRECTO SIN RELLENO]".
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
            return None, f"Error de API Gemini: {response.status_code} - {response.text}", None
    except Exception as e:
        return None, f"Error durante la generación con IA: {str(e)}", None

def extract_sources_from_script(script_text):
    """
    Extracts source information from the script text.
    Looks for lines starting with 'Fuente:', 'Sources:', etc.
    """
    if not script_text:
        return ""
    
    import re
    # Look for "Fuente: X" or "Source: X"
    # Capture the rest of the line
    match = re.search(r'(?:Fuente|Source|Basado en):\s*(.*)', script_text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
        
    return ""

def extract_hashtags_from_script(script_text):
    """
    Extracts hashtags from the script text.
    """
    if not script_text:
        return ""
        
    import re
    # Find all words starting with #
    hashtags = re.findall(r'#\w+', script_text)
    
    # Return as space-separated string unique tags
    unique_tags = list(set(hashtags))
    return " ".join(unique_tags)

class ProjectLogger:
    def __init__(self, project):
        self.project = project
        self.log_buffer = []

    def log(self, message):
        print(f"[Project {self.project.id}] {message}")
        self.log_buffer.append(message)
        self.project.log_output = "\n".join(self.log_buffer)
        self.project.save(update_fields=['log_output'])

async def generate_audio_edge(text, output_path, voice="es-ES-AlvaroNeural"):
    import edge_tts
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def generate_video_process(project):
    """
    Smart router that detects script format and calls appropriate engine:
    - JSON format → AVGL v4.0 engine (video_engine.py)
    - Legacy format → Old column-based engine (kept for backwards compatibility)
    """
    import json
    from .video_engine import generate_video_avgl
    
    # Try to detect JSON format
    script_text = project.script_text.strip()
    
    # Remove markdown code blocks if present (common copy-paste error)
    if script_text.startswith('```'):
        # Remove first line (```json or ```)
        script_text = script_text.split('\n', 1)[1]
        # Remove last line if it is ```
        if script_text.strip().endswith('```'):
            script_text = script_text.rsplit('```', 1)[0]
    
    script_text = script_text.strip()
    
    # If it starts with {, assume IT IS JSON and report errors if invalid
    if script_text.startswith('{'):
        try:
            json.loads(script_text)
            print(f"[Project {project.id}] Detected AVGL v4.0 JSON format")
            return generate_video_avgl(project)
        except json.JSONDecodeError as e:
            # IT IS JSON, BUT INVALID. DO NOT FALLBACK TO LEGACY.
            logger = ProjectLogger(project)
            logger.log(f"❌ Error CRÍTICO en formato JSON: {e}")
            logger.log(f"   Línea {e.lineno}: {e.msg}")
            project.status = 'error'
            project.save()
            return  # Stop here
            
    # If not JSON, assume legacy
    print(f"[Project {project.id}] Detected legacy column format")
    return generate_video_legacy(project)


def generate_video_legacy(project):
    """
    Legacy video generation for column-based format: TITULO | IMAGEN | TEXTO
    Kept for backwards compatibility.
    """
    from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, VideoFileClip, CompositeAudioClip, afx
    logger = ProjectLogger(project)
    logger.log(f"Starting generation for project: {project.title}")
    
    project.status = 'processing'
    project.save()
    
    try:
        # Determine voice
        voice_to_use = project.voice_id
        if project.engine == 'edge':
            if not voice_to_use:
                voice_to_use = os.getenv("EDGE_VOICE", "es-ES-AlvaroNeural")
        else:
            if not voice_to_use:
                voice_to_use = os.getenv("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")

        # Parse Script
        sections = []
        lines = project.script_text.strip().split('\n')
        
        for line in lines:
            if not line.strip():
                continue
            parts = line.strip().split('|')
            if len(parts) == 3:
                image_name = parts[1].strip()
                # Check assets folder
                image_path = os.path.join(settings.MEDIA_ROOT, 'assets', image_name)
                
                # If source path is defined, prioritize it
                if project.source_path and os.path.exists(project.source_path):
                    local_path = os.path.join(project.source_path, image_name)
                    if os.path.exists(local_path):
                        image_path = local_path
                
                sections.append({
                    "title": parts[0].strip(),
                    "image": image_path,
                    "text": parts[2].strip(),
                    "original_image_name": image_name 
                })
        
        if not sections:
            raise Exception("No valid sections found in script")

        clips = []
        temp_audio_dir = os.path.join(settings.MEDIA_ROOT, 'temp_audio')
        os.makedirs(temp_audio_dir, exist_ok=True)
        
        # Get fallback images
        available_images = []
        
        # Add local path images to fallback if available
        if project.source_path and os.path.exists(project.source_path):
             available_images.extend([
                os.path.join(project.source_path, f) 
                for f in os.listdir(project.source_path) 
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.mp4', '.mov', '.avi'))
            ])
            
        assets_dir = os.path.join(settings.MEDIA_ROOT, 'assets')
        if os.path.exists(assets_dir):
            available_images.extend([
                os.path.join(assets_dir, f) 
                for f in os.listdir(assets_dir) 
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.mp4', '.mov', '.avi'))
            ])

        for i, section in enumerate(sections):
            logger.log(f"Processing section {i+1}: {section['title']}")
            
            # Audio
            audio_path = os.path.join(temp_audio_dir, f"{project.id}_audio_{i}.mp3")
            
            if project.engine == 'edge':
                # NEW (v3.0.1): Support cleaned emotions in legacy mode
                from .avgl_engine import translate_emotions, wrap_ssml
                
                # Default rate for legacy is from .env (usually +15%) or overridden here
                rate = os.getenv("EDGE_RATE", "+0%")
                
                # Use clean mode (use_ssml=False) to avoid instructions leakage
                clean_text = translate_emotions(section['text'], use_ssml=False)
                # wrap_ssml will see no tags and return text as is
                final_text = wrap_ssml(clean_text, voice_to_use, rate)
                
                # Run async in sync context safely
                try:
                    asyncio.run(generate_audio_edge(final_text, audio_path, voice_to_use))
                except RuntimeError:
                    # Fallback if there is already a running loop in this thread
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(generate_audio_edge(final_text, audio_path, voice_to_use))
                    loop.close()
            else:
                from elevenlabs.client import ElevenLabs
                from elevenlabs import save
                api_key = os.getenv("ELEVENLABS_API_KEY")
                if not api_key:
                    raise Exception("ElevenLabs API Key not found")
                client = ElevenLabs(api_key=api_key)
                audio_gen = client.text_to_speech.convert(
                    text=section['text'],
                    voice_id=voice_to_use,
                    model_id="eleven_multilingual_v2"
                )
                save(audio_gen, audio_path)
            
            # Load audio
            if not os.path.exists(audio_path):
                 logger.log("Audio not generated. Skipping.")
                 continue

            try:
                audio_clip = AudioFileClip(audio_path)
                if not hasattr(audio_clip, 'rate') and hasattr(audio_clip, 'fps'):
                    audio_clip.rate = audio_clip.fps
                duration = audio_clip.duration + 0.5
            except Exception as e:
                logger.log(f"Error loading audio: {e}")
                continue

            # Image/Video Asset
            asset_path = section['image']
            used_fallback = False
            
            if not os.path.exists(asset_path):
                logger.log(f"Asset not found: {section['original_image_name']}")
                if available_images:
                    asset_path = random.choice(available_images)
                    used_fallback = True
                    logger.log(f"Using fallback: {os.path.basename(asset_path)}")
                else:
                    logger.log("No fallback available. Skipping.")
                    continue
            
            # Create Clip
            try:
                # Set dynamic resolution
                if project.aspect_ratio == 'portrait':
                    TARGET_SIZE = (1080, 1920)
                else:
                    TARGET_SIZE = (1920, 1080)
                
                is_video = asset_path.lower().endswith(('.mp4', '.mov', '.avi', '.webm'))
                if is_video:
                    video_clip = VideoFileClip(asset_path).resized(TARGET_SIZE)
                    if video_clip.duration < duration:
                        loops = int(duration / video_clip.duration) + 1
                        val_clip = concatenate_videoclips([video_clip] * loops, method="chain")
                        video_clip = val_clip.subclipped(0, duration)
                    else:
                        video_clip = video_clip.subclipped(0, duration)
                    final_clip = video_clip.with_audio(audio_clip)
                else:
                    final_clip = ImageClip(asset_path).resized(TARGET_SIZE).with_duration(duration).with_audio(audio_clip)
                
                clips.append(final_clip)
            except Exception as e:
                logger.log(f"Error creating clip: {e}")
        
        if clips:
            logger.log("Concatenating clips with optimized method...")
            # Use method="chain" which is MUCH faster than "compose"
            # This requires all clips to have the same size, which we ensured above.
            final_video = concatenate_videoclips(clips, method="chain")
            
            # --- Background Music Integration ---
            if project.background_music:
                try:
                    logger.log(f"Adding background music: {project.background_music.name}")
                    bg_music_path = project.background_music.file.path
                    if os.path.exists(bg_music_path):
                        bg_audio = AudioFileClip(bg_music_path)
                        
                        # Loop music to cover video duration
                        loops = int(final_video.duration / bg_audio.duration) + 1
                        bg_audio_looped = bg_audio.with_effects([afx.AudioLoop(n_loops=loops)]).with_duration(final_video.duration)
                        
                        # Set volume (using music_volume field)
                        bg_audio_final = bg_audio_looped.with_effects([afx.MultiplyVolume(project.music_volume)])
                        
                        # Mix with original audio
                        # final_video already has the voice audio from concatenate_videoclips
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
            
            logger.log("Writing final video file with multi-threading...")
            import multiprocessing
            n_threads = multiprocessing.cpu_count()
            
            final_video.write_videofile(
                output_full_path, 
                fps=24, 
                logger=None, 
                threads=n_threads,
                preset="superfast",
                codec="libx264",
                audio_codec="aac"
            )
            
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
            logger.log("Video generation successful!")
        else:
            project.status = 'failed'
            logger.log("No clips were generated.")

    except Exception as e:
        logger.log(f"Critical Error: {str(e)}")
        import traceback
        logger.log(traceback.format_exc())
        project.status = 'failed'
    
    project.save()
