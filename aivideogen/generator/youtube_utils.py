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

def upload_video(youtube, video_path, title, description, category_id="28", privacy_status="unlisted"):
    """
    Uploads a video to YouTube.
    category_id "28" is Science & Technology.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': ['noticias', 'ia', 'ciencias'],
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
    
    fixed_hashtags_str = os.getenv(
        'YOUTUBE_FIXED_HASHTAGS',
        '#IA #notiaci #ciencia #tecnologia #noticias #avances #avancesmedicos #carlosramirez #descubrimientos'
    ).strip()
    
    # Clean quotes
    if (fixed_hashtags_str.startswith('"') and fixed_hashtags_str.endswith('"')) or \
       (fixed_hashtags_str.startswith("'") and fixed_hashtags_str.endswith("'")):
        fixed_hashtags_str = fixed_hashtags_str[1:-1].strip()
    
    script_hashtags_str = extract_hashtags_from_script(project.script_text)
    
    if script_hashtags_str:
        all_hashtags = script_hashtags_str + " " + fixed_hashtags_str
        description_parts.append(all_hashtags)
    else:
        description_parts.append(fixed_hashtags_str)
    
    description_parts.append("")
    
    # 6. Promotion
    description_parts.append("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    description_parts.append("🤖 Este video ha sido generado automáticamente por nuestra aplicación aiVideoGen")
    description_parts.append("")
    description_parts.append("📧 Para más información contáctanos:")
    description_parts.append("carlosaipro6@gmail.com")
    
    return "\n".join(description_parts)
