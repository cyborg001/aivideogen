import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from django.conf import settings
from .models import YouTubeToken

# Scopes needed for YouTube upload
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_flow():
    client_secrets_file = os.path.join(settings.BASE_DIR, 'client_secrets.json')
    
    # Check if the file exists
    if not os.path.exists(client_secrets_file):
        raise FileNotFoundError(
            f"⚠️ El archivo 'client_secrets.json' no existe en {settings.BASE_DIR}.\n\n"
            "Para habilitar la integración con YouTube, necesitas:\n"
            "1. Ir a https://console.cloud.google.com/\n"
            "2. Crear un proyecto y habilitar la YouTube Data API v3\n"
            "3. Crear credenciales OAuth 2.0 (Aplicación de escritorio)\n"
            "4. Descargar el archivo JSON de credenciales\n"
            "5. Renombrarlo a 'client_secrets.json'\n"
            "6. Colocarlo en la carpeta raíz del proyecto\n\n"
            "Consulta la documentación para más detalles."
        )
    
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        client_secrets_file,
        scopes=SCOPES,
        redirect_uri=settings.YOUTUBE_REDIRECT_URI
    )
    return flow

def get_youtube_client():
    token_obj = YouTubeToken.objects.last()
    if not token_obj:
        return None
    
    credentials = google.oauth2.credentials.Credentials(**token_obj.token)
    
    # Check if we need to refresh (client-side simple check, better handled by library)
    # The dictionary 'token' expected by Credentials(**token) usually has everything
    
    youtube = build('youtube', 'v3', credentials=credentials)
    return youtube

def upload_video(youtube, video_path, title, description, category_id="28", privacy_status="unlisted", tags=None):
    """
    Uploads a video to YouTube.
    category_id "28" is Science & Technology.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if tags is None:
        tags = ['noticias', 'ia', 'ciencias']

    try:
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status
            }
        }

        media = MediaFileUpload(
            video_path,
            chunksize=1024*1024,
            resumable=True
        )

        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                logger.info(f"[YouTube] Subiendo... {progress}%")
                print(f"[YouTube] Uploaded {progress}%")
        
        logger.info(f"[YouTube] Upload completado - Response: {response}")
        return response
    except Exception as e:
        logger.error(f"[YouTube] Error durante upload: {str(e)}")
        raise

def generate_youtube_description(project):
    """
    Generates a professional description for YouTube based on project data.
    """
    from .utils import extract_sources_from_script, extract_hashtags_from_script
    
    description_parts = []
    
    # 1. Welcome
    description_parts.append("👋 ¡Hola! Bienvenido a Notiaci")
    description_parts.append("")
    
    # 2. Project Title
    description_parts.append(f"🎬 {project.title}")
    description_parts.append("")
    
    # 3. Sources
    script_sources = extract_sources_from_script(project.script_text)
    if script_sources:
        description_parts.append("📚 FUENTES:")
        description_parts.append(script_sources)
        description_parts.append("")
    
    # 4. Timestamps (Chapters)
    if project.timestamps and project.timestamps.strip():
        description_parts.append("📍 CAPÍTULOS:")
        description_parts.append(project.timestamps)
        description_parts.append("")
    
    # 5. Hashtags
    description_parts.append("🏷️ TAGS:")
    
    from .utils import extract_hashtags_from_script, generate_contextual_tags
    
    fixed_hashtags_str = os.getenv(
        'YOUTUBE_FIXED_HASHTAGS',
        '#IA #notiaci #ciencia #tecnologia #noticias #avances #avancesmedicos #carlosramirez #descubrimientos'
    ).strip()
    
    # Clean quotes
    if (fixed_hashtags_str.startswith('"') and fixed_hashtags_str.endswith('"')) or \
       (fixed_hashtags_str.startswith("'") and fixed_hashtags_str.endswith("'")):
        fixed_hashtags_str = fixed_hashtags_str[1:-1].strip()
    
    # Build list of all hashtags
    all_hashtags_list = []
    
    # Add script hashtags
    script_hashtags_str = extract_hashtags_from_script(project.script_text)
    if script_hashtags_str:
        all_hashtags_list.extend([h for h in script_hashtags_str.split() if h.startswith('#')])
    
    # Add contextual hashtags
    context_tags = generate_contextual_tags(project)
    all_hashtags_list.extend([f"#{t}" for t in context_tags])
    
    # Add fixed hashtags
    all_hashtags_list.extend([h for h in fixed_hashtags_str.split() if h.startswith('#')])
    
    # Deduplicate and format
    final_hashtags = " ".join(dict.fromkeys(all_hashtags_list))
    description_parts.append(final_hashtags)
    
    description_parts.append("")
    
    # 6. Promotion
    description_parts.append("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    description_parts.append("🤖 Este video ha sido generado automáticamente por nuestra aplicación aiVideoGen")
    description_parts.append("")
    description_parts.append("📧 Para más información contáctanos:")
    description_parts.append("carlosaipro6@gmail.com")
    
    return "\n".join(description_parts)

def trigger_auto_upload(project):
    """
    Handles the coordination of video upload for a project.
    Safe to call from background thread.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # 1. Check if authorized
    try:
        youtube = get_youtube_client()
    except Exception as e:
        logger.error(f"[YouTube] Error obteniendo cliente para subida automática: {e}")
        return False

    if not youtube:
        project.log_output += "\n[YouTube] ⚠️ No se pudo realizar la subida automática: No hay token de autorización. Debes autorizar al menos una vez manualmente."
        project.save(update_fields=['log_output'])
        return False
        
    # 2. Check if already uploaded
    if project.youtube_video_id:
        return True
        
        # 3. Prepare metadata
    try:
        title = project.title
        description = generate_youtube_description(project)
        
        # EXTRACT TAGS LOGIC (v4.2 - Smart Contextual Tags)
        from .utils import extract_hashtags_from_script, generate_contextual_tags
        
        # 1. Script/Manual Tags
        script_tags_str = project.script_hashtags or extract_hashtags_from_script(project.script_text)
        tags_list = [t.strip().replace('#', '') for t in script_tags_str.split() if t.strip()]
        
        # 2. Automatic Contextual Tags (Extracted from title/content)
        contextual_tags = generate_contextual_tags(project)
        tags_list.extend(contextual_tags)
        
        # 3. Fixed Global Tags (.env)
        fixed_tags = settings.YOUTUBE_FIXED_HASHTAGS
        # Clean quotes
        if (fixed_tags.startswith('"') and fixed_tags.endswith('"')) or \
           (fixed_tags.startswith("'") and fixed_tags.endswith("'")):
            fixed_tags = fixed_tags[1:-1].strip()
        tags_list.extend([t.strip().replace('#', '') for t in fixed_tags.split() if t.strip()])
        
        # Deduplicate and limit
        final_tags = list(dict.fromkeys(tags_list))[:20]

        # 4. Upload
        logger.info(f"[YouTube] Iniciando subida automática para proyecto {project.id}: {title}")
        project.log_output += f"\n[YouTube] 🚀 Iniciando subida con Tags Contextuales: {', '.join(final_tags[:5])}..."
        project.save(update_fields=['log_output'])
        
        result = upload_video(youtube, project.output_video.path, title, description, tags=final_tags)
        
        if result and 'id' in result:
             video_id = result['id']
             video_url = f"https://www.youtube.com/watch?v={video_id}"
             project.youtube_video_id = video_id
             project.log_output += f"\n[YouTube] ✅ Video subido con éxito!\nURL: {video_url}"
             project.save()
             logger.info(f"[YouTube] Subida automática exitosa - Video ID: {video_id}")
             return True
        else:
            project.log_output += "\n[YouTube] ⚠️ La subida terminó pero no se recibió confirmación de ID."
            project.save(update_fields=['log_output'])
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"[YouTube] Error en subida automática: {error_msg}")
        project.log_output += f"\n[YouTube] ❌ Error en subida automática: {error_msg}"
        project.save(update_fields=['log_output'])
        
    return False
