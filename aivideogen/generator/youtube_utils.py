import os
import re
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from django.conf import settings
from .models import YouTubeToken

# Scopes needed for YouTube upload and GDrive sync
SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/drive.file'
]

def get_flow():
    secrets_filename = settings.GOOGLE_CLIENT_SECRETS_FILE
    client_secrets_file = os.path.join(settings.BASE_DIR, secrets_filename)
    
    # Check if the file exists
    if not os.path.exists(client_secrets_file):
        raise FileNotFoundError(
            f"⚠️ El archivo '{secrets_filename}' no existe en {settings.BASE_DIR}.\n\n"
            "Para habilitar la integración con YouTube, necesitas:\n"
            "1. Ir a https://console.cloud.google.com/\n"
            "2. Crear un proyecto y habilitar la YouTube Data API v3\n"
            "3. Crear credenciales OAuth 2.0 (Aplicación de escritorio)\n"
            "4. Descargar el archivo JSON de credenciales\n"
            "5. Renombrarlo a '{secrets_filename}' (o el valor definido en su .env)\n"
            "6. Colocarlo en la carpeta raíz del proyecto\n\n"
            "Consulta la documentación para más detalles."
        )
    
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        client_secrets_file,
        scopes=SCOPES
    )
    # Ensure redirect_uri is set after loading, very important for 'web' type
    flow.redirect_uri = settings.YOUTUBE_REDIRECT_URI
    
    # v15.1: Force consent so the user can actually switch accounts if they are logged in.
    # We add this to the authorization_url later, but we can set it here if needed.
    return flow

def get_youtube_client():
    from google.auth.transport.requests import Request
    
    token_obj = YouTubeToken.objects.last()
    if not token_obj:
        return None
    
    credentials = google.oauth2.credentials.Credentials(**token_obj.token)
    
    # Check if we need to refresh
    if credentials.expired and credentials.refresh_token:
        try:
            credentials.refresh(Request())
            # Update the stored token with new values
            token_obj.token = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
            token_obj.save()
        except Exception as e:
            # If refresh fails, it might be truly revoked/expired
            import logging
            logger = logging.getLogger(__name__)
            error_msg = str(e)
            if 'invalid_grant' in error_msg.lower():
                logger.error(f"❌ [YouTube] ERROR CRÍTICO: El token ha expirado o ha sido revocado. DEBES RE-AUTORIZAR la cuenta en la interfaz de la Web App.")
            else:
                logger.error(f"[YouTube] Falló el refresh automático: {e}")
            return None
    
    youtube = build('youtube', 'v3', credentials=credentials)
    return youtube

def get_youtube_channel_info(youtube):
    """
    Recupera el nombre y el link del canal autenticado.
    v20.1: Proporciona transparencia al Arquitecto sobre el destino del video.
    """
    try:
        request = youtube.channels().list(
            part="snippet,contentDetails",
            mine=True
        )
        response = request.execute()
        if response.get('items'):
            item = response['items'][0]
            title = item['snippet']['title']
            channel_id = item['id']
            return {
                'title': title,
                'url': f"https://www.youtube.com/channel/{channel_id}"
            }
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"[YouTube] No se pudo obtener info del canal: {e}")
    
    return {'title': "Cuenta Autorizada", 'url': "https://www.youtube.com"}

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
        error_msg = str(e)
        if "quotaExceeded" in error_msg:
             logger.error(f"⚠️ [YouTube] LÍMITE DE CUOTA EXCEDIDO: YouTube ha bloqueado la subida por hoy (límite de 10,000 unidades API).")
             raise Exception("Límite de cuota de YouTube excedido. Intenta de nuevo mañana.")
        logger.error(f"[YouTube] Error durante upload: {error_msg}")
        raise

def generate_youtube_description(project):
    from .utils import extract_sources_from_script, extract_hashtags_from_script, get_human_title
    
    description_parts = []
    
    # 1. Welcome
    description_parts.append("👋 ¡Hola! Bienvenidos a mi canal")
    description_parts.append("")
    
    # 2. Project Title (Humanized)
    human_title = get_human_title(project.title)
    description_parts.append(f"🎬 {human_title}")
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
        '' # v15.3: Si no hay en .env, dejamos vacío para que actúe el placeholder en la UI
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
    
    # v19.2: Removed aiVideoGen promotional footer (YouTube policy violation risk)
    final_description = "\n".join(description_parts)
    
    # 7. TAG STRIPPING (v8.7)
    # Limpiar [PHO]pronunciacion|subtitulo[/PHO] -> subtitulo
    final_description = re.sub(r'\[PHO\][^|]*\|([^\]]*)\[/PHO\]', r'\1', final_description)
    # Limpiar [SUB]texto[/SUB] -> texto
    final_description = re.sub(r'\[SUB\](.*?)\[/SUB\]', r'\1', final_description)
    # Eliminar cualquier otra etiqueta entre corchetes (emociones, etc.)
    final_description = re.sub(r'\[[A-Z0-9_-]+\]', '', final_description)
    
    return final_description

def trigger_auto_upload(project):
    """
    Handles the coordination of video upload for a project.
    Safe to call from background thread.
    """
    import logging
    from datetime import datetime
    logger = logging.getLogger(__name__)
    
    # 1. Check if authorized
    try:
        youtube = get_youtube_client()
    except Exception as e:
        logger.error(f"[YouTube] Error obteniendo cliente para subida automática: {e}")
        return False

        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        project.log_output += f"\n[{now}] [YouTube] [WARNING] No se pudo realizar la subida automática: No hay token de autorización."
        project.save(update_fields=['log_output'])
        return False
        
    # v13.5: Support for multiple uploads (User Request)
    # Replaced blocking check with just a log if it exists
    if project.youtube_video_id:
        logger.info(f"[YouTube] Proyecto {project.id} ya tiene IDs previos: {project.youtube_video_id}")
        
    # 3. Prepare metadata (v7.0: Humanization Priority)
    try:
        from .utils import get_human_title, get_viral_title_from_json
        
        # Priority order: 1. Manual editing, 2. JSON title, 3. DB Title (Cleaned)
        json_viral_title = get_viral_title_from_json(project)
        title = project.social_title or json_viral_title or get_human_title(project.title)
        
        description = project.social_description or generate_youtube_description(project)
        
        # EXTRACT TAGS LOGIC (v4.2 - Smart Contextual Tags)
        from .utils import extract_hashtags_from_script, generate_contextual_tags
        
        if project.social_tags:
            # Si el usuario editó los tags manualmente, usarlos directamente (separados por coma)
            final_tags = [t.strip().replace('#', '') for t in project.social_tags.split(',') if t.strip()]
        else:
            # 1. Script/Manual Tags
            script_tags_str = project.script_hashtags or extract_hashtags_from_script(project.script_text)
            tags_list = [t.strip().replace('#', '') for t in script_tags_str.split() if t.strip()]
            
            # 2. Automatic Contextual Tags
            contextual_tags = generate_contextual_tags(project)
            tags_list.extend(contextual_tags)
            
            # 3. Fixed Global Tags (.env)
            fixed_tags = settings.YOUTUBE_FIXED_HASHTAGS
            if (fixed_tags.startswith('"') and fixed_tags.endswith('"')) or \
               (fixed_tags.startswith("'") and fixed_tags.endswith("'")):
                fixed_tags = fixed_tags[1:-1].strip()
            tags_list.extend([t.strip().replace('#', '') for t in fixed_tags.split() if t.strip()])
            
            final_tags = list(dict.fromkeys(tags_list))[:20]
 
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # v20.1: Transparency Enhancement - Log Channel Info
        channel_info = get_youtube_channel_info(youtube)
        channel_name = channel_info['title']
        channel_url = channel_info['url']
        
        logger.info(f"[YouTube] Iniciando subida para proyecto {project.id}: {title} | Canal: {channel_name}")
        project.log_output += f"\n[{now}] [YouTube] [START] Subiendo a canal: '{channel_name}' ({channel_url})"
        project.log_output += f"\n[{now}] [YouTube] [START] Iniciando subida con Tags: {', '.join(final_tags[:3])}..."
        project.save(update_fields=['log_output'])
        
        result = upload_video(youtube, project.output_video.path, title, description, tags=final_tags)
        
        if result and 'id' in result:
             video_id = result['id']
             video_url = f"https://www.youtube.com/watch?v={video_id}"
             
             # v13.5: ID with Timestamp (Append strategy)
             timestamp = datetime.now().strftime('%d/%m %H:%M')
             entry = f"{video_id} ({timestamp})"
             
             if project.youtube_video_id:
                 # Accumulate multiple IDs separated by space or newline
                 project.youtube_video_id = f"{project.youtube_video_id} | {entry}"
             else:
                 project.youtube_video_id = entry
                 
             from datetime import datetime
             now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
             project.log_output += f"\n[{now}] [YouTube] [SUCCESS] Video subido con éxito!\nURL: {video_url}"
             project.save(update_fields=['youtube_video_id', 'log_output'])
             logger.info(f"[YouTube] Subida exitosa - Video ID: {video_id}")
             return True
        else:
            from datetime import datetime
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            project.log_output += f"\n[{now}] [YouTube] [WARNING] La subida terminó sin confirmación de ID."
            project.save(update_fields=['log_output'])
            
    except Exception as e:
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.error(f"[YouTube] Error en subida: {error_msg}")
        project.log_output += f"\n[{now}] [YouTube] [ERROR] Error en subida: {error_msg}"
        project.save(update_fields=['log_output'])
        
    return False
def get_project_social_copy(project):
    """
    Generates unified social metadata for manual uploading.
    Includes Description, Tags, and a pinned Comment.
    v15.3: Si no hay info social en .env, devolvemos vacío para usar placeholders en UI.
    """
    from .utils import get_human_title
    import os

    # Check if we have social configuration in .env
    has_env_config = bool(os.getenv('YOUTUBE_FIXED_HASHTAGS'))
    
    if not has_env_config:
        # Modo Manual (Placeholders): Devolvemos vacío para que la UI use su texto de ejemplo
        return {
            'title': get_human_title(project.title),
            'description': '',
            'tags': '',
            'pinned_comment': ''
        }

    # 1. Title & Description
    title = project.social_title or get_human_title(project.title)
    description = project.social_description or generate_youtube_description(project)
    
    # 2. Extract Tags (Formatted for Studio copy-paste)
    from .utils import extract_hashtags_from_script, generate_contextual_tags
    
    if project.social_tags:
        tags_for_studio = project.social_tags
        # Extraer para el comentario fijado
        final_tags = [t.strip() for t in project.social_tags.split(',') if t.strip()]
    else:
        script_tags_str = project.script_hashtags or extract_hashtags_from_script(project.script_text)
        tags_list = [t.strip().replace('#', '') for t in script_tags_str.split() if t.strip()]
        
        contextual_tags = generate_contextual_tags(project)
        tags_list.extend(contextual_tags)
        
        fixed_tags = settings.YOUTUBE_FIXED_HASHTAGS
        if (fixed_tags.startswith('"') and fixed_tags.endswith('"')) or \
           (fixed_tags.startswith("'") and fixed_tags.endswith("'")):
            fixed_tags = fixed_tags[1:-1].strip()
        tags_list.extend([t.strip().replace('#', '') for t in fixed_tags.split() if t.strip()])
        
        final_tags = list(dict.fromkeys(tags_list))[:20]
        tags_for_studio = ", ".join(final_tags)
    
    # 3. Pinned Comment
    # v14.0 Pattern: Thanks + Highlights + Call to Action
    if project.social_pinned_comment:
        pinned_comment = project.social_pinned_comment
    else:
        comment_parts = []
        comment_parts.append(f"¡Gracias por ver! Si te gustó el video sobre '{title}', déjanos un comentario con tu opinión. 👇")
        comment_parts.append("")
        # Add top 3 tags as hashtags in comment
        comment_hashtags = " ".join([f"#{t.replace(' ', '')}" for t in final_tags[:5]])
        comment_parts.append(comment_hashtags)
        comment_parts.append("")
        comment_parts.append("¡No olvides suscribirte para más noticias de IA y ciencia! 🚀")
        
        pinned_comment = "\n".join(comment_parts)
    
    return {
        'title': title,
        'description': description,
        'tags': tags_for_studio,
        'pinned_comment': pinned_comment
    }
