from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from .models import Asset, VideoProject, YouTubeToken, Music, SFX
from .utils import generate_video_process
from .youtube_utils import get_flow, get_youtube_client, upload_video
import threading
import os
import logging
import time

# Heartbeat tracking for auto-shutdown
LAST_ACTIVITY_FILE = os.path.join(settings.BASE_DIR, 'last_activity.txt')

def update_last_activity():
    try:
        with open(LAST_ACTIVITY_FILE, 'w') as f:
            f.write(str(time.time()))
    except Exception as e:
        logger.warning(f"Failed to update heartbeat file: {e}")

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
            filetypes=[("JSON/Text", "*.json *.txt"), ("All files", "*.*")]
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
        script_hashtags = request.POST.get('script_hashtags', '').strip()
        
        background_music = None
        if music_id:
            background_music = Music.objects.get(id=music_id)
            
            # SYNC UI -> JSON SCRIPT (User Request)
            # If user selected music in UI, force it into the JSON script
            if script:
                try:
                    import json
                    script_json = json.loads(script)
                    
                    # Update fields
                    # We use the filename/name for the script reference
                    script_json['background_music'] = background_music.name
                    script_json['music_volume'] = float(music_volume)
                    
                    # Save back to string
                    script = json.dumps(script_json, indent=4, ensure_ascii=False)
                except Exception as e:
                    # If script isn't valid JSON, we can't inject. Proceed as is.
                    print(f"Error syncing music to JSON: {e}")
        
        # If script is empty but source path and script file are provided, try to load it
        if not script and source_path and script_file:
            try:
                full_path = os.path.join(source_path, script_file)
                if os.path.exists(full_path):
                    # CRITICAL: Do NOT read file content into script_text here if we want to rely on the file.
                    # Or read it just for immediate caching, but ensure source_path is set.
                    # The `source_path` is already passed in POST and saved to the model.
                    # We just need to make sure `source_path` points to the FILE if it's a file selection.
                    
                    # Fix: backend expects source_path to be the asset root usually, but here it might be the script specific path?
                    # In `create.html`, browse_script returns `path` (dir) and `filename`.
                    # The POST sends `source_path` (dir) and `script_file` (filename).
                    
                    # We should concatenate them for the Project.source_path if we want strictly file-based.
                    # But the model says source_path is "folder containing script and assets".
                    # However, my new `_get_script_file_path` handles directory input by looking for [title].json.
                    # But if we have the specific filename, we should probably save it.
                    
                    # Let's save the FULL path to source_path if it's a specific script file project.
                    source_path = full_path 
                    
                    with open(full_path, 'r', encoding='utf-8') as f:
                        script = f.read()
                        
                        # Apply Sync Logic here too if loaded from file late
                        if background_music:
                            try:
                                import json
                                script_json = json.loads(script)
                                script_json['background_music'] = background_music.name
                                script_json['music_volume'] = float(music_volume)
                                # We DO Update the file content in memory (and potentially save back? No, let's just initialize the DB text)
                                script = json.dumps(script_json, indent=4, ensure_ascii=False)
                            except: pass
            except Exception as e:
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
            script_hashtags=script_hashtags,
            auto_upload_youtube=auto_upload,
            render_mode=request.POST.get('render_mode', 'cpu')
        )
        
        # NOTE: Auto-start removed by user request (v2.25.0)
        # User must click "Generar" in detail view.
        
        return redirect('generator:project_detail', project_id=project.id)
        
    # v2.18.0 - Load default script from external file
    default_script_path = os.path.join(settings.BASE_DIR, 'docs', 'EJEMPLOS', 'guion_defecto.json')
    default_script = ""
    
    try:
        if os.path.exists(default_script_path):
            with open(default_script_path, 'r', encoding='utf-8') as f:
                default_script = f.read().strip()
                logger.debug("[System] Guion de defecto cargado desde archivo JSON.")
        else:
            # Emergency fallback if file is missing
            default_script = '{"title": "Nuevo Proyecto", "blocks": []}'
            logger.warning(f"[Warning] Archivo de defecto no encontrado en {default_script_path}")
    except Exception as e:
        default_script = "{}"
        logger.error(f"[Error] Error cargando guion de defecto: {e}")

    # 1. OPTIONAL: Overwrite with news suggestion or specific example if needed
    # (Existing logic below handles news_id and retry)
    news_id = request.GET.get('news_id')
    ai_generated_script = ""
    ai_visual_prompts = ""
    initial_title = ""

    if news_id:
        from researcher.models import NewsItem
        from .utils import generate_script_ai
        news_item = get_object_or_404(NewsItem, id=news_id)
        initial_title = news_item.title[:200]
        
        script, prompts, music_suggestion, ai_hashtags = generate_script_ai(news_item)
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
            ai_hashtags = ""
    else:
        ai_hashtags = ""

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
                'visual_prompts': retry_project.visual_prompts or '',
                'script_hashtags': retry_project.script_hashtags or ''
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
        'ai_hashtags': ai_hashtags,
        'initial_title': initial_title,
        'all_music': all_music,
        'retry_data': retry_data  # Pass retry data to template
    })

def project_detail(request, project_id):
    project = get_object_or_404(VideoProject, id=project_id)
    return render(request, 'generator/detail.html', {'project': project})

def delete_project(request, project_id):
    project = get_object_or_404(VideoProject, id=project_id)
    if request.method == 'POST':
        # 1. Stop if running
        if project.status in ['processing', 'pending']:
             project.status = 'cancelled'
             project.save()
        
        # 2. Cleanup Files
        if project.output_video and project.output_exists:
            try: os.remove(project.output_video.path)
            except: pass
            
        if project.thumbnail and os.path.exists(project.thumbnail.path):
            try: os.remove(project.thumbnail.path)
            except: pass
            
        # 3. Delete DB Record
        project.delete()
        messages.success(request, "Proyecto eliminado y archivos limpiados.")
    return redirect('generator:home')

def start_project(request, project_id):
    """Manually starts the video generation process."""
    project = get_object_or_404(VideoProject, id=project_id)
    
    if request.method == 'POST':
        if project.status == 'processing':
            messages.warning(request, "El proyecto ya se está procesando.")
        else:
            # Reset logs/status
            project.status = 'processing'
            project.log_output = "🚀 Iniciando generación manual (v3.3)..."
            project.save()
            
            # Start Thread
            thread = threading.Thread(target=generate_video_process, args=(project,))
            thread.daemon = True
            thread.start()
            
            messages.success(request, "Generación iniciada.")
            
    return redirect('generator:project_detail', project_id=project.id)

def reset_project(request, project_id):
    """Deletes existing output and resets status to pending."""
    project = get_object_or_404(VideoProject, id=project_id)
    if request.method == 'POST':
        # 1. Cleanup Files
        if project.output_video and project.output_exists:
            try: os.remove(project.output_video.path)
            except: pass
        if project.thumbnail and os.path.exists(project.thumbnail.path):
            try: os.remove(project.thumbnail.path)
            except: pass
            
        # 2. Reset Status/Metadata
        project.status = 'pending'
        project.output_video = None
        project.thumbnail = None
        project.timestamps = ""
        project.log_output = "♻️ Proyecto reiniciado para nueva generación."
        project.save()
        
        messages.success(request, "Proyecto reiniciado. Puedes volver a generarlo ahora.")
    return redirect('generator:project_detail', project_id=project.id)

def clone_project(request, project_id):
    """Creates a deep copy of the project and its settings."""
    original = get_object_or_404(VideoProject, id=project_id)
    if request.method == 'POST':
        # Deep Copy
        new_project = VideoProject.objects.create(
            title=f"{original.title} (Copia)",
            script_text=original.script_text,
            engine=original.engine,
            aspect_ratio=original.aspect_ratio,
            voice_id=original.voice_id,
            background_music=original.background_music,
            music_volume=original.music_volume,
            source_path=original.source_path,
            visual_prompts=original.visual_prompts,
            script_hashtags=original.script_hashtags,
            auto_upload_youtube=original.auto_upload_youtube,
            status='pending'
        )
        
        messages.success(request, f"Versión clonada: {new_project.title}")
        return redirect('generator:project_detail', project_id=new_project.id)
    return redirect('generator:project_detail', project_id=original.id)

def stop_project(request, project_id):
    project = get_object_or_404(VideoProject, id=project_id)
    if request.method == 'POST':
        if project.status == 'processing' or project.status == 'pending':
            project.status = 'cancelled'
            project.log_output += "\n🛑 GENERACIÓN DETENIDA POR EL USUARIO."
            project.save()
            messages.info(request, "Generación cancelada. El proceso se detendrá en el próximo paso seguro.")
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
            include_granted_scopes='true',
            prompt='consent'
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
    
    if not project.output_video or not project.output_exists:
        messages.error(request, "❌ El video aún no se ha generado o el archivo no existe.")
        return redirect('generator:project_detail', project_id=project.id)

    try:
        from .youtube_utils import trigger_auto_upload, get_youtube_client
        
        # Check authorization first for better user feedback
        if not get_youtube_client():
            messages.warning(request, "⚠️ Primero debes autorizar tu cuenta de YouTube.")
            return redirect('generator:youtube_authorize')

        # Use the shared logic
        success = trigger_auto_upload(project)
        
        if success and project.youtube_video_id:
            video_url = f"https://www.youtube.com/watch?v={project.youtube_video_id}"
            return render(request, 'generator/youtube_upload_success.html', {
                'video_url': video_url,
                'fallback_url': request.build_absolute_uri('/')
            })
        else:
            # Errors are already logged to project.log_output by trigger_auto_upload
            messages.error(request, "❌ No se pudo subir el video. Revisa el log del proyecto para más detalles.")
            return redirect('generator:project_detail', project_id=project.id)
            
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

# -------------------------------------------------------------------------
# VISUAL SCRIPT EDITOR (Feature: visual-editor)
# -------------------------------------------------------------------------

@csrf_exempt
def create_project_from_editor(request):
    """API: Creates a new project from the provided JSON script and settings."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        script = data.get('script', {})
        settings = data.get('settings', {})
        
        # Determine Title
        title = settings.get('title') or script.get('title') or "Nuevo Proyecto"
        
        # Cleanup Title (Reuse logic from create_project)
        import re
        title = re.sub(r'^[^\w\s]*\s*(GUION|TÍTULO|TITLE|SCENE|ESCENA)\s*:?\s*', '', title, flags=re.IGNORECASE).strip()
        
        # Determine Voice (fallback chain)
        voice_id = settings.get('voice_id') or script.get('voice') or ""
        
        from .models import VideoProject
        project = VideoProject.objects.create(
            title=title,
            status='pending',
            script_text=json.dumps(script, indent=4, ensure_ascii=False),
            voice_id=voice_id,
            aspect_ratio=settings.get('aspect_ratio') or script.get('aspect_ratio', 'landscape'),
            music_volume=float(settings.get('music_volume', 0.15)),
            auto_upload_youtube=bool(settings.get('auto_upload', False)),
            render_mode=settings.get('render_mode') or script.get('render_mode', 'cpu')
        )
        
        # Handle Music
        bg_music_input = settings.get('background_music') or script.get('background_music')
        if bg_music_input:
            from .models import Music
            bg_music_name = os.path.basename(bg_music_input)
            m = Music.objects.filter(file__iexact=bg_music_input).first() or \
                Music.objects.filter(name__iexact=bg_music_name).first() or \
                Music.objects.filter(file__icontains=bg_music_name).first()
            if m:
                project.background_music = m
                project.save()
        
        return JsonResponse({'status': 'created', 'project_id': project.id})
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating project from editor: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)

def project_editor(request, project_id):
    """Renders the main visual editor interface."""
    project = get_object_or_404(VideoProject, id=project_id)
    return render(request, 'generator/project_editor.html', {'project': project})

@csrf_exempt
def json_to_text_api(request):
    """API: Converts JSON script to legacy-style text (preserving metadata)."""
    if request.method != 'POST': return JsonResponse({'error': 'POST required'}, status=405)
    try:
        import json
        from .avgl_engine import convert_avgl_json_to_text
        data = json.loads(request.body)
        text = convert_avgl_json_to_text(data)
        return JsonResponse({'text': text})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def text_to_json_api(request):
    """API: Converts legacy-style text (with tags) back to structured JSON."""
    if request.method != 'POST': return JsonResponse({'error': 'POST required'}, status=405)
    try:
        import json
        from .avgl_engine import convert_text_to_avgl_json
        data = json.loads(request.body)
        text = data.get('text', '')
        title = data.get('title', 'Imported Script')
        json_data = convert_text_to_avgl_json(text, title=title)
        return JsonResponse(json_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def get_project_script_json(request, project_id):
    """API: Returns the project script as JSON. Auto-validates/initializes."""
    project = get_object_or_404(VideoProject, id=project_id)
    import json
    from .avgl_engine import convert_text_to_avgl_json

    data = {}
    try:
        # Try parse as JSON
        data = json.loads(project.script_text)
    except:
        # Fallback: Convert text -> JSON on fly
        if project.script_text:
            try:
                data = convert_text_to_avgl_json(project.script_text, title=project.title)
            except Exception as e:
                return JsonResponse({'error': f"Failed to convert script: {str(e)}"}, status=400)
    
    # --- AUTO-REPAIR ASSETS ---
    repaired = False
    for block in data.get('blocks', []):
        for scene in block.get('scenes', []):
            for asset in scene.get('assets', []):
                # Case 1: ID is missing, but TYPE contains the filename (Legacy Bug)
                if not asset.get('id') and asset.get('type') and '.' in asset['type']:
                    asset['id'] = asset['type']
                    asset['type'] = 'video' if asset['id'].lower().endswith(('.mp4', '.mov', '.avi')) else 'image'
                    repaired = True
                # Case 2: Both present but ID is generic while TYPE has filename
                elif asset.get('id') in ['image', 'video'] and asset.get('type') and '.' in asset['type']:
                    asset['id'] = asset['type']
                    asset['type'] = 'video' if asset['id'].lower().endswith(('.mp4', '.mov', '.avi')) else 'image'
                    repaired = True
    
    return JsonResponse(data, safe=False)

@csrf_exempt
def save_project_script_json(request, project_id):
    """API: Saves the sent JSON back to the project script_text."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    project = get_object_or_404(VideoProject, id=project_id)
    try:
        import json
        data = json.loads(request.body)
        
        # 1. Update Script JSON
        script_data = data
        if 'script' in data:
            script_data = data['script']
        
        project.script_text = json.dumps(script_data, indent=4, ensure_ascii=False)
        
        # 2. Update Project Settings (if present)
        if 'settings' in data:
            settings_data = data['settings']
            
            if 'title' in settings_data:
                project.title = settings_data['title']
                
            if 'music_volume' in settings_data:
                try: 
                    project.music_volume = float(settings_data['music_volume'])
                except: 
                    pass
            
            if 'aspect_ratio' in settings_data:
                project.aspect_ratio = settings_data['aspect_ratio']
                
            # Global Music (filename string)
            if 'background_music' in settings_data:
                bg_music_input = settings_data['background_music']
                if not bg_music_input:
                     project.background_music = None
                else:
                     from .models import Music
                     bg_music_name = os.path.basename(bg_music_input)
                     # Try exact match first, then by name (extracted), then contains
                     m = Music.objects.filter(file__iexact=bg_music_input).first() or \
                         Music.objects.filter(name__iexact=bg_music_name).first() or \
                         Music.objects.filter(file__icontains=bg_music_name).first()
                     if m: project.background_music = m

            # Global Voice ID
            if 'voice_id' in settings_data:
                project.voice_id = settings_data['voice_id']

            # Auto Upload
            if 'auto_upload' in settings_data:
                project.auto_upload_youtube = bool(settings_data['auto_upload'])

            # Render Mode (v4.7)
            if 'render_mode' in settings_data:
                project.render_mode = settings_data['render_mode']

        project.save()
        return JsonResponse({'status': 'saved', 'title': project.title})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def scene_form(request, project_id):
    """HTMX: Returns the modal form content for adding/editing a scene."""
    # Context data from GET params (pre-fill)
    index = request.GET.get('index', '') # If empty -> Add Mode
    
    # Normally we'd fetch scene data from DB, but here the Frontend 
    # will pass data into the form via JS or we construct an empty one.
    # For now, we render a generic form.
    

# -------------------------------------------------------------------------
# STANDALONE SCRIPT EDITOR (Feature: independent-editor)
# -------------------------------------------------------------------------

def script_editor_standalone(request):
    """Renders the editor without a project context."""
    return render(request, 'generator/project_editor.html', {
        'project': None, # No project
        'is_standalone': True
    })

# -------------------------------------------------------------------------
# LOG VIEWER (Feature: web-logs)
# -------------------------------------------------------------------------

def view_logs(request):
    """Renders the application logs from app.log."""
    log_file = os.path.join(settings.BASE_DIR, 'app.log')
    logs = []
    
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
                # Read last 500 lines
                lines = f.readlines()
                logs = lines[-500:]
                logs.reverse() # Show newest first
        except Exception as e:
            logs = [f"Error leyendo el archivo de logs: {e}"]
    else:
        logs = ["No se encontró el archivo app.log. Asegúrate de que la aplicación haya generado algún evento."]
        
    return render(request, 'generator/logs.html', {'logs': logs})

@csrf_exempt
def api_heartbeat(request):
    """Updates the last activity timestamp to prevent auto-shutdown."""
    update_last_activity()
    return JsonResponse({'status': 'ok', 'time': time.time()})

@csrf_exempt
def save_script_file(request):
    """API: Saves JSON content to a local file using Save As dialog."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
        
    try:
        import json
        import tkinter as tk
        from tkinter import filedialog
        
        data = json.loads(request.body)
        script_content = data.get('script', {})
        
        # Tkinter UI
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        # Default Initial Dir
        initial_dir = r"c:\Users\Usuario\Documents\curso creacion contenido con ia\guiones"
        if not os.path.exists(initial_dir):
            try: os.makedirs(initial_dir)
            except: pass

        file_path = filedialog.asksaveasfilename(
            initialdir=initial_dir,
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            confirmoverwrite=True,
            title="Guardar Guion como..."
        )
        
        root.destroy()
        
        if not file_path:
            return JsonResponse({'status': 'cancelled'})
            
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(script_content, f, indent=4, ensure_ascii=False)
            
        return JsonResponse({
            'status': 'saved',
            'filename': os.path.basename(file_path),
            'path': file_path
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def browse_local_asset(request):
    """API: Opens file dialog via an external process to pick an asset and returns absolute path."""
    import subprocess
    import json
    import sys
    
    try:
        filter_type = request.GET.get('type', 'visual') # 'visual' or 'audio'
        
        # Use sys.executable to ensure we use the same python environment
        helper_path = os.path.join(settings.BASE_DIR, 'generator', 'browse_helper.py')
        
        result = subprocess.run(
            [sys.executable, helper_path, filter_type],
            capture_output=True,
            text=True,
            timeout=300 # 5 minute timeout
        )
        
        if result.returncode != 0:
            return JsonResponse({'error': f"Helper failed: {result.stderr}"}, status=500)
            
        # Extract JSON from stdout (in case of warnings/extra output)
        out = result.stdout.strip()
        try:
            start_idx = out.find('{')
            end_idx = out.rfind('}') + 1
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in output")
            json_str = out[start_idx:end_idx]
            data = json.loads(json_str)
        except Exception as e:
            return JsonResponse({'error': f"Failed to parse helper output: {out}. Error: {e}"}, status=500)
            
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def download_project_script_json(request, project_id):
    """
    Downloads the project's script_text as a .json file.
    """
    from django.http import HttpResponse
    from django.utils.text import slugify
    
    project = get_object_or_404(VideoProject, id=project_id)
    script_content = project.script_text
    
    response = HttpResponse(script_content, content_type='application/json')
    safe_title = slugify(project.title) or f"project_{project.id}"
    response['Content-Disposition'] = f'attachment; filename="{safe_title}.json"'
    return response

def toggle_auto_upload(request, project_id):
    """
    Toggles the auto_upload_youtube flag for a project.
    """
    project = get_object_or_404(VideoProject, id=project_id)
    project.auto_upload_youtube = not project.auto_upload_youtube
    project.save()
    
    status_str = "ACTIVADA" if project.auto_upload_youtube else "DESACTIVADA"
    project.log_output += f"\\n[System] 🔄 Subida automática {status_str} por el usuario."
    project.save(update_fields=['log_output', 'auto_upload_youtube'])
    
    # Handle AJAX requests from detail page (v3.5)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
         return JsonResponse({'status': 'success', 'enabled': project.auto_upload_youtube})
         
    messages.success(request, f"Subida automática a YouTube: {status_str}")
    return redirect('generator:project_detail', project_id=project.id)
