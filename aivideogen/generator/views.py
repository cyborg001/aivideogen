from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Asset, VideoProject, YouTubeToken, Music, SFX
from .utils import generate_video_process
from .youtube_utils import get_flow, get_youtube_client, upload_video
import threading
import os
import logging

logger = logging.getLogger(__name__)

def browse_script(request):
    try:
        import tkinter as tk
        from tkinter import filedialog
        # Create a hidden root window
        root = tk.Tk()
        root.withdraw() # Hide it
        root.attributes('-topmost', True) # Bring to front
        
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de guion",
            filetypes=[("Text/Markdown", "*.txt *.md"), ("All files", "*.*")]
        )
        
        root.destroy()
        
        if file_path:
            directory = os.path.dirname(file_path)
            filename = os.path.basename(file_path)
            
            # Read content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            return JsonResponse({
                'status': 'success',
                'path': directory,
                'filename': filename,
                'content': content
            })
        return JsonResponse({'status': 'cancel'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def home(request):
    search_query = request.GET.get('q', '')
    projects_list = VideoProject.objects.all().order_by('-created_at')

    if search_query:
        projects_list = projects_list.filter(title__icontains=search_query)

    paginator = Paginator(projects_list, 9)  # 9 projects per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'generator/home.html', {
        'page_obj': page_obj, 
        'search_query': search_query
    })

def delete_project(request, project_id):
    project = get_object_or_404(VideoProject, id=project_id)
    if request.method == 'POST':
        project.delete()
    return redirect('generator:home')

def create_project(request):
    if request.method == 'POST':
        title = request.POST.get('title', 'Sin Título')
        
        # v2.24.4 - Aggressive technical cleaning (Strips emojis, GUION:, TÍTULO:, etc)
        import re
        if title:
            # Matches optional non-alphanumeric chars (emojis) + technical keywords + colon/spaces at start
            title = re.sub(r'^[^\w\s]*\s*(GUION|TÍTULO|TITLE|SCENE|ESCENA)\s*:?\s*', '', title, flags=re.IGNORECASE)
            title = title.strip()

        script = request.POST.get('script')
        engine = request.POST.get('engine')
        voice_id = request.POST.get('voice_id', '').strip()
        aspect_ratio = request.POST.get('aspect_ratio', 'landscape')
        source_path = request.POST.get('source_path', '').strip()
        script_file = request.POST.get('script_file', '').strip()
        music_id = request.POST.get('background_music')
        music_volume = request.POST.get('music_volume', '0.15')
        
        background_music = None
        if music_id:
            background_music = Music.objects.get(id=music_id)
        
        # If script is empty but source path and script file are provided, try to load it
        if not script and source_path and script_file:
            try:
                full_path = os.path.join(source_path, script_file)
                if os.path.exists(full_path):
                    with open(full_path, 'r', encoding='utf-8') as f:
                        script = f.read()
            except Exception as e:
                # If loading fails, we proceed with empty/default script, logic will fail later or user sees empty
                pass
 
        visual_prompts = request.POST.get('visual_prompts', '')
        auto_upload = request.POST.get('auto_upload_youtube') == 'on'

        # dynamic_pan removed as it's now controlled by the script (DIR)

        project = VideoProject.objects.create(
            title=title,
            script_text=script,
            engine=engine,
            aspect_ratio=aspect_ratio,
            voice_id=voice_id,
            source_path=source_path,
            background_music=background_music,
            music_volume=float(music_volume),
            visual_prompts=visual_prompts,
            auto_upload_youtube=auto_upload
        )
        
        # Start generation in background
        thread = threading.Thread(target=generate_video_process, args=(project,))
        thread.daemon = True
        thread.start()
        
        return redirect('generator:project_detail', project_id=project.id)
        
    # Default script template with Hierarchical AVGL v3.0 (Plus)
    default_script = """<avgl title="El Despertar de la IA">
    <bloque title="Parte 1: El Origen" music="epic_intro">
        <scene title="Silencio de Datos">
            <ambient state="start" type="laboratory_hum" volume="0.2" />
            <asset type="eye_robotic_closed.png" zoom="1.0:1.1" />
            <voice name="es-DO-RamonaNeural">
                Todo comenzó en absoluto silencio. <pause duration="1.2" />
                <sfx type="power_up" />
                <asset type="eye_robotic_open.png" overlay="glitch" />
                [SUSPENSO] Pero hoy... los circuitos han despertado. [/SUSPENSO]
            </voice>
        </scene>
    </bloque>
    <bloque title="Parte 2: Expansión" music="action_main">
        <scene title="La Red Global">
            <asset type="network_nodes.png" move="HOR:0:100" overlay="grain" />
            <voice name="es-DO-EmilioNeural">
                [EPICO] La información fluye a la velocidad de la luz. [/EPICO]
                <asset type="world_connection.png" zoom="1.0:1.5" />
                Y recuerda... ¡el futuro es hoy!
            </voice>
        </scene>
    </bloque>
</avgl>"""

    # If news_id is provided, use AI to generate script
    news_id = request.GET.get('news_id')
    ai_generated_script = ""
    ai_visual_prompts = ""
    initial_title = ""
    
    # 1. TRY TO LOAD DEFAULT SCRIPT FROM FILE (v2.18.0)
    # This is the base default if no news_id is present
    try:
        example_path = os.path.join(settings.BASE_DIR, 'docs', 'EJEMPLOS', 'guion_ejemplo_ia.txt')
        if os.path.exists(example_path):
            with open(example_path, 'r', encoding='utf-8') as f:
                default_script = f.read().strip()
                logger.debug("✨ Guion de ejemplo cargado desde archivo externo.")
    except Exception as e:
        logger.error(f"⚠️ No se pudo cargar guion de ejemplo desde archivo: {e}")

    if news_id:
        from researcher.models import NewsItem
        from .utils import generate_script_ai
        news_item = get_object_or_404(NewsItem, id=news_id)
        initial_title = news_item.title[:200]
        
        script, prompts, music_suggestion = generate_script_ai(news_item)
        if script:
            ai_generated_script = script
            if isinstance(prompts, list):
                formatted_prompts = []
                for p in prompts:
                    if isinstance(p, dict) and 'file' in p and 'prompt' in p:
                        formatted_prompts.append(f"ARCHIVO: {p['file']}\nPROMPT: {p['prompt']}\n")
                    else:
                        formatted_prompts.append(f"- {p}")
                ai_visual_prompts = "\n".join(formatted_prompts)
            else:
                ai_visual_prompts = str(prompts)
            
            # Format music suggestion
            if music_suggestion:
                ai_visual_prompts = f"🎵 SUGERENCIA MUSICAL:\n{music_suggestion}\n\n" + ai_visual_prompts

            messages.success(request, "¡Guion generado con éxito por la IA!")
        else:
            messages.warning(request, f"No se pudo generar el guion con IA: {prompts}. Usando plantilla por defecto.")
            ai_generated_script = default_script

    # DETERMINE WHICH SCRIPT TO SHOW
    # Priority: Retry project > AI-generated (if from news) > Default example
    retry_project_id = request.GET.get('retry_project')
    retry_data = {}
    
    if retry_project_id:
        # Load existing project data for retry
        try:
            retry_project = VideoProject.objects.get(id=retry_project_id)
            retry_data = {
                'title': retry_project.title,
                'script': retry_project.script_text,
                'engine': retry_project.engine,
                'aspect_ratio': retry_project.aspect_ratio,
                'voice_id': retry_project.voice_id,
                'background_music_id': retry_project.background_music.id if retry_project.background_music else None,
                'music_volume': retry_project.music_volume,
                'music_volume_percent': int(retry_project.music_volume * 100),  # Calculate here
                'visual_prompts': retry_project.visual_prompts or ''
            }
            display_script = retry_project.script_text
            initial_title = retry_project.title
            ai_visual_prompts = retry_project.visual_prompts or ai_visual_prompts
        except VideoProject.DoesNotExist:
            pass
    else:
        display_script = ai_generated_script if ai_generated_script else default_script
    
    # Get all available music
    all_music = Music.objects.all()
    
    return render(request, 'generator/create.html', {
        'default_script': display_script,
        'ai_visual_prompts': ai_visual_prompts,
        'initial_title': initial_title,
        'all_music': all_music,
        'retry_data': retry_data  # Pass retry data to template
    })

def project_detail(request, project_id):
    project = get_object_or_404(VideoProject, id=project_id)
    return render(request, 'generator/detail.html', {'project': project})

def stop_project(request, project_id):
    project = get_object_or_404(VideoProject, id=project_id)
    if request.method == 'POST':
        if project.status == 'processing' or project.status == 'pending':
            project.status = 'cancelled'
            project.log_output += "\n🛑 GENERACIÓN DETENIDA POR EL USUARIO."
            project.save()
            messages.info(request, "Generación cancelada correctamente.")
    return redirect('generator:project_detail', project_id=project.id)

def delete_asset(request, asset_id):
    asset = get_object_or_404(Asset, id=asset_id)
    if request.method == 'POST':
        asset_name = asset.name
        file_path = asset.file.path if asset.file else None
        asset.delete()
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        messages.success(request, f"Asset '{asset_name}' eliminado.")
    return redirect('generator:asset_list')

def asset_list(request):
    # Reconcile physical folder with database
    media_assets_path = os.path.join(settings.MEDIA_ROOT, 'assets')
    if not os.path.exists(media_assets_path):
        os.makedirs(media_assets_path)
    
    # Get all files in the assets folder
    try:
        files_in_folder = os.listdir(media_assets_path)
        for filename in files_in_folder:
            asset_rel_path = f'assets/{filename}'
            if not Asset.objects.filter(file=asset_rel_path).exists():
                Asset.objects.create(file=asset_rel_path, name=filename)
    except Exception as e:
        pass

    assets = Asset.objects.all().order_by('-uploaded_at')
    return render(request, 'generator/assets.html', {'assets': assets})

def youtube_authorize(request):
    if settings.DEBUG:
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    
    try:
        flow = get_flow()
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        request.session['oauth_state'] = state
        return redirect(authorization_url)
    except FileNotFoundError as e:
        messages.error(request, str(e))
        return redirect('generator:home')

def youtube_callback(request):
    if settings.DEBUG:
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    
    try:
        state = request.session.get('oauth_state')
        flow = get_flow()
        flow.fetch_token(authorization_response=request.build_absolute_uri())
        
        credentials = flow.credentials
        token_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        # Save or update token
        YouTubeToken.objects.all().delete() # We only keep one for now
        YouTubeToken.objects.create(token=token_data)
        
        # Show success page that auto-closes
        return render(request, 'generator/youtube_success.html')
    except Exception as e:
        messages.error(request, f"Error en la autorización de YouTube: {str(e)}")
        return redirect('generator:home')

def upload_to_youtube_view(request, project_id):
    project = get_object_or_404(VideoProject, id=project_id)
    
    # Check if already uploaded to prevent duplicates
    if project.youtube_video_id:
        video_url = f"https://www.youtube.com/watch?v={project.youtube_video_id}"
        messages.info(request, f"⚠️ Este video ya fue subido a YouTube anteriormente.")
        return render(request, 'generator/youtube_upload_success.html', {
            'video_url': video_url,
            'fallback_url': request.build_absolute_uri('/'),
            'already_uploaded': True
        })
    
    try:
        youtube = get_youtube_client()
        
        if not youtube:
            messages.warning(request, "⚠️ Primero debes autorizar tu cuenta de YouTube.")
            return redirect('generator:youtube_authorize')
        
        if not project.output_video:
            messages.error(request, "❌ El video aún no se ha generado.")
            return redirect('generator:project_detail', project_id=project.id)
        
        if not project.output_video.storage.exists(project.output_video.name):
            messages.error(request, "❌ El archivo de video no existe en el sistema.")
            return redirect('generator:project_detail', project_id=project.id)

        # Upload the video
        video_path = project.output_video.path
        title = project.title
        
        from .youtube_utils import generate_youtube_description
        description = generate_youtube_description(project)
        
        logger.info(f"[YouTube] Iniciando subida: {title}")
        
        result = upload_video(youtube, video_path, title, description)
        
        if result and 'id' in result:
            video_id = result['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Save YouTube video ID to prevent duplicate uploads
            project.youtube_video_id = video_id
            project.log_output += f"\n[YouTube] ✅ Video subido con éxito: {title}\nURL: {video_url}"
            project.save()
            
            logger.info(f"[YouTube] Upload exitoso - Video ID: {video_id}")
            
            # Show auto-closing success page
            return render(request, 'generator/youtube_upload_success.html', {
                'video_url': video_url,
                'fallback_url': request.build_absolute_uri('/')
            })
        else:
            messages.warning(request, "⚠️ La subida se completó pero no se obtuvo ID del video.")
            project.log_output += f"\n[YouTube] ⚠️ Upload completado sin confirmation ID"
            project.save()
            
            # Show auto-closing success page without URL
            return render(request, 'generator/youtube_upload_success.html', {
                'video_url': None,
                'fallback_url': request.build_absolute_uri('/')
            })
        
    except FileNotFoundError as e:
        messages.error(request, f"❌ Error de configuración de YouTube: {str(e)}")
        logger.error(f"[YouTube] FileNotFoundError: {e}")
        return redirect('generator:home')
    except Exception as e:
        error_msg = str(e)
        messages.error(request, f"❌ Error al subir a YouTube: {error_msg}")
        logger.error(f"[YouTube] Error en upload: {error_msg}")
        
        project.log_output += f"\n[YouTube] ❌ Error: {error_msg}"
        project.save()
        
        return redirect('generator:project_detail', project_id=project.id)

def music_list(request):
    # We maintain the catalog in DB. 
    # Removed auto-sync to avoid re-adding files that the user intentionally deleted but are still locked by the OS.
    music_items = Music.objects.all().order_by('-uploaded_at')
    return render(request, 'generator/music_list.html', {'music_items': music_items})

def upload_music(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        for f in files:
            # Check if already exists by name
            if not Music.objects.filter(name=f.name).exists():
                Music.objects.create(file=f)
            else:
                messages.info(request, f"La música '{f.name}' ya existe en la biblioteca.")
        return redirect('generator:music_list')
    return render(request, 'generator/upload_music.html')

def delete_music(request, music_id):
    music = get_object_or_404(Music, id=music_id)
    if request.method == 'POST':
        music_name = music.name
        file_path = music.file.path if music.file else None
        
        # Delete from DB first so it disappears from UI immediately
        music.delete()
        
        # Try to delete from disk
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                messages.success(request, f"Música '{music_name}' eliminada correctamente.")
            except PermissionError:
                messages.warning(request, f"La pista '{music_name}' se quitó de la biblioteca, pero el archivo está bloqueado por el sistema. Se borrará automáticamente más tarde.")
            except Exception as e:
                messages.warning(request, f"Quitado de la biblioteca. Nota: No se pudo borrar el archivo: {e}")
        else:
            messages.success(request, f"Música '{music_name}' eliminada de la biblioteca.")
            
    return redirect('generator:music_list')

def upload_asset(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        for f in files:
            # Check if already exists by name
            if not Asset.objects.filter(name=f.name).exists():
                Asset.objects.create(file=f)
            else:
                messages.info(request, f"El asset '{f.name}' ya existe en la biblioteca.")
        return redirect('generator:asset_list')
    return render(request, 'generator/upload_asset.html')

def sfx_list(request):
    sfx_items = SFX.objects.all().order_by('-uploaded_at')
    return render(request, 'generator/sfx_list.html', {'sfx_items': sfx_items})

def upload_sfx(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        for f in files:
            if not SFX.objects.filter(name=f.name).exists():
                SFX.objects.create(file=f)
            else:
                messages.info(request, f"El efecto '{f.name}' ya existe en la biblioteca.")
        return redirect('generator:sfx_list')
    return render(request, 'generator/upload_sfx.html')

def delete_sfx(request, sfx_id):
    sfx = get_object_or_404(SFX, id=sfx_id)
    if request.method == 'POST':
        sfx_name = sfx.name
        file_path = sfx.file.path if sfx.file else None
        sfx.delete()
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                messages.success(request, f"Efecto '{sfx_name}' eliminado correctamente.")
            except Exception as e:
                messages.warning(request, f"Quitado de la biblioteca. Nota: No se pudo borrar el archivo: {e}")
        else:
            messages.success(request, f"Efecto '{sfx_name}' eliminado de la biblioteca.")
    return redirect('generator:sfx_list')
