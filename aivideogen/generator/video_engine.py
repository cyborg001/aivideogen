"""
AVGL v4.0 - Video Generation Engine
Handles the complete video rendering pipeline with optimizations
"""

import os
import time
import re
import numpy as np
from django.conf import settings


# ═══════════════════════════════════════════════════════════════════
# Ken Burns Effect (Optimized with Pre-Scaling)
# ═══════════════════════════════════════════════════════════════════

def apply_ken_burns(image_path, duration, target_size, zoom="1.0:1.0", move="HOR:50:50", overlay_path=None, fit=False):
    """
    Applies optimized Ken Burns effect with pre-scaling.
    
    Args:
        image_path: Path to the image
        duration: Duration in seconds
        target_size: (width, height) tuple
        zoom: "start:end" zoom factor (e.g., "1.0:1.3")
        move: "DIR:start:end" pan direction (e.g., "HOR:0:100")
        overlay_path: Optional overlay video path
        fit: If True, fit image within frame (no crop) and disable Ken Burns
    
    Returns:
        VideoClip with Ken Burns effect applied
    """
    from moviepy import ImageClip, VideoFileClip, CompositeVideoClip, vfx
    from PIL import Image
    
    # ═══════════════════════════════════════════════════════════════════
    # FIT MODE (Static, No Crop)
    # ═══════════════════════════════════════════════════════════════════
    if fit:
        img = Image.open(image_path)
        img_w_orig, img_h_orig = img.size
        
        # Calculate scale to FIT within target
        scale_factor = min(target_size[0] / img_w_orig, target_size[1] / img_h_orig)
        new_size = (int(img_w_orig * scale_factor), int(img_h_orig * scale_factor))
        
        # Resize
        img_resized = img.resize(new_size, Image.Resampling.LANCZOS)
        img_np = np.array(img_resized)
        
        # Create clip centered on black background
        clip = ImageClip(img_np, duration=duration)
        
        # Create background (black)
        bg_np = np.zeros((target_size[1], target_size[0], 3), dtype=np.uint8)
        bg_clip = ImageClip(bg_np, duration=duration)
        
        # Composite
        final_clip = CompositeVideoClip([bg_clip, clip.with_position("center")], size=target_size)
    
        # Apply overlay if specified
        if overlay_path and os.path.exists(overlay_path):
            overlay = VideoFileClip(overlay_path, has_mask=True)
            overlay = overlay.with_effects([vfx.Loop(duration=duration)])
            overlay = overlay.resized(target_size)
            final_clip = CompositeVideoClip([final_clip, overlay], size=target_size)
            
        return final_clip

    # ═══════════════════════════════════════════════════════════════════
    # KEN BURNS MODE (Crop & Pan)
    # ═══════════════════════════════════════════════════════════════════
    
    # Parse zoom parameters
    zoom_parts = zoom.split(':') if zoom else ['1.0', '1.0']
    zoom_start = float(zoom_parts[0]) if len(zoom_parts) > 0 else 1.0
    zoom_end = float(zoom_parts[1]) if len(zoom_parts) > 1 else zoom_start
    
    # Parse move parameters
    move_parts = move.split(':') if move else ['HOR', '50', '50']
    move_dir = move_parts[0] if len(move_parts) > 0 else 'HOR'
    move_start = int(move_parts[1]) if len(move_parts) > 1 else 50
    move_end = int(move_parts[2]) if len(move_parts) > 2 else move_start
    
    # OPTIMIZATION: Pre-scale image to working size (preserves aspect ratio)
    img = Image.open(image_path)
    img_w_orig, img_h_orig = img.size
    
    # Calculate scale needed to cover/fit target at zoom=1.0
    scale_factor_cover = max(target_size[0] / img_w_orig, target_size[1] / img_h_orig)
    
    # We want extra resolution for zoom
    max_zoom = max(zoom_start, zoom_end)
    working_scale = scale_factor_cover * max_zoom * 1.2  # 1.2x buffer (reduced from 1.5x for RAM)
    
    working_w = int(img_w_orig * working_scale)
    working_h = int(img_h_orig * working_scale)
    working_size = (working_w, working_h)
    
    # Resize once (High quality)
    img_resized = img.resize(working_size, Image.Resampling.LANCZOS)
    img_np = np.array(img_resized)
    
    # Update dimensions for calc
    img_h, img_w = img_np.shape[:2]
    target_w, target_h = target_size
    scale_to_cover = max(target_w / img_w, target_h / img_h)
    
    def get_frame_scale(t):
        """Calculate zoom at time t"""
        progress = t / duration
        relative_zoom = zoom_start + (zoom_end - zoom_start) * progress
        return scale_to_cover * relative_zoom
    
    def get_frame_pos(t):
        """Calculate position at time t"""
        progress = t / duration
        scale = get_frame_scale(t)
        
        # Calculate scaled dimensions
        scaled_w = img_w * scale
        scaled_h = img_h * scale
        
        # Calculate position based on movement
        if move_dir.upper() == 'HOR':
            # Horizontal pan
            pos_start_pct = move_start / 100.0
            pos_end_pct = move_end / 100.0
            current_pct = pos_start_pct + (pos_end_pct - pos_start_pct) * progress
            
            max_offset_x = (scaled_w - target_w) / 2
            x = (target_w / 2) - (scaled_w / 2) + (max_offset_x * (2 * current_pct - 1))
            y = (target_h - scaled_h) / 2
        else:
            # Vertical pan
            pos_start_pct = move_start / 100.0
            pos_end_pct = move_end / 100.0
            current_pct = pos_start_pct + (pos_end_pct - pos_start_pct) * progress
            
            max_offset_y = (scaled_h - target_h) / 2
            x = (target_w - scaled_w) / 2
            y = (target_h / 2) - (scaled_h / 2) + (max_offset_y * (2 * current_pct - 1))
        
        return (x, y)
    
    # Create ImageClip from pre-scaled array
    base_clip = ImageClip(img_np, duration=duration)
    
    # ═══════════════════════════════════════════════════════════════════
    # KEN BURNS IMPLEMENTATION
    # ═══════════════════════════════════════════════════════════════════
    # In MoviePy 2.x, we use fl (frame lambda) or resized with a function
    # that returns the new (w, h) tuple.
    
    def resizer(t):
        scale = get_frame_scale(t)
        return (int(img_w * scale), int(img_h * scale))

    # Apply dynamic resizing and positioning
    clip = base_clip.resized(resizer)
    clip = clip.with_position(get_frame_pos)
    
    # Apply overlay if specified
    if overlay_path and os.path.exists(overlay_path):
        overlay = VideoFileClip(overlay_path, has_mask=True)
        # Fix: use vfx.Loop instead of .loop()
        overlay = overlay.with_effects([vfx.Loop(duration=duration)])
        overlay = overlay.resized(target_size)
        clip = CompositeVideoClip([clip, overlay], size=target_size)
    
    return clip


# ═══════════════════════════════════════════════════════════════════
# Main Video Generation Function
# ═══════════════════════════════════════════════════════════════════

def generate_video_avgl(project):
    """
    Main video generation function using AVGL v4.0 JSON format.
    Includes performance optimizations:
    - Pre-scaled Ken Burns
    - Overlay caching
    - Parallel audio generation (if asyncio available)
    """
    from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, VideoFileClip, CompositeAudioClip
    from .avgl_engine import parse_avgl_json, translate_emotions, wrap_ssml, generate_audio_edge, generate_audio_elevenlabs
    from .utils import ProjectLogger  # Import existing logger
    import asyncio
    import numpy as np
    
    # Initialize
    start_time = time.time()
    project.status = 'processing'
    project.save()
    
    # Use ProjectLogger from utils.py (saves to DB)
    logger = ProjectLogger(project)
    logger.log("🚀 Iniciando generación AVGL v4.0")
    
    # Parse script
    try:
        script = parse_avgl_json(project.script_text)
        logger.log(f"✅ Script parseado: '{script.title}'")
    except Exception as e:
        logger.log(f"❌ Error al parsear JSON: {e}")
        project.status = 'error'
        project.save()
        return
    
    # Update project title if specified
    if script.title and script.title != "Video Sin Título":
        project.title = script.title
        project.save()
    
    # Setup directories
    temp_audio_dir = os.path.join(settings.MEDIA_ROOT, 'temp_audio')
    os.makedirs(temp_audio_dir, exist_ok=True)
    assets_dir = os.path.join(settings.MEDIA_ROOT, 'assets')
    overlay_dir = os.path.join(settings.MEDIA_ROOT, 'overlays')
    
    # Target resolution
    target_size = (1080, 1920) if project.aspect_ratio == 'portrait' else (1920, 1080)
    
    # Overlay cache (OPTIMIZATION)
    overlay_cache = {}
    
    # Generate audio for all scenes
    logger.log("🎙️ Generando audio...")
    all_scenes = script.get_all_scenes()
    audio_files = []
    
    for i, scene in enumerate(all_scenes):
        logger.log(f"  Escena {i+1}/{len(all_scenes)}: {scene.title}")
        
        if not scene.text:
            continue
        
        # Prepare text - Use clean mode (no SSML) for Edge TTS to prevent instructions leakage
        # until the service-side SSML issues are resolved.
        use_ssml = (project.engine == 'eleven') # ElevenLabs handles tags/strips them safely
        text_with_emotions = translate_emotions(scene.text, use_ssml=use_ssml)
        
        # Generate audio
        audio_path = os.path.join(temp_audio_dir, f"project_{project.id}_scene_{i:03d}.mp3")
        
        if project.engine == 'edge':
            # Edge TTS supports SSML
            speed_rate = f"+{int((scene.speed - 1.0) * 100)}%"
            ssml_text = wrap_ssml(text_with_emotions, scene.voice, speed_rate)
            
            # DEBUG LOGS
            logger.log(f"  🔍 Text Raw: {scene.text[:50]}...")
            if ssml_text.startswith('<speak'):
                logger.log(f"  🔍 SSML Generated: {ssml_text[:100]}...")
            
            # Run async
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(
                generate_audio_edge(ssml_text, audio_path, scene.voice, speed_rate)
            )
            loop.close()
            
            if not success:
                logger.log(f"❌ Error crítico generando audio para escena '{scene.title}'")
                project.status = 'error'
                project.save()
                return # Stop generation
        else:
            # ElevenLabs
            api_key = os.getenv('ELEVENLABS_API_KEY')
            if not api_key:
                logger.log("❌ ELEVENLABS_API_KEY no configurada")
                project.status = 'error'
                project.save()
                return
            
            voice_id = os.getenv('ELEVENLABS_VOICE_ID', 'EXAVITQu4vr4xnSDxMaL')
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(
                generate_audio_elevenlabs(text_with_emotions, audio_path, voice_id, api_key)
            )
            loop.close()
        
        if success:
            audio_files.append((scene, audio_path))
        else:
            logger.log(f"  ⚠️ Error generando audio para escena {i+1}")
    
    # Update project with music if defined in script but not in project
    if not project.background_music and script.blocks and script.blocks[0].music:
        from .models import Music
        try:
            m_name = script.blocks[0].music
            # Try to find music by filename or name
            m_obj = Music.objects.filter(file__icontains=m_name).first()
            if m_obj:
                project.background_music = m_obj
                project.save()
        except:
            pass
    
    # Generate video clips
    logger.log("🎬 Generando clips de video...")
    clips = []
    current_time = 0
    timestamps_list = []
    
    for scene, audio_path in audio_files:
        # Get audio duration
        audio_clip = AudioFileClip(audio_path)
        total_scene_duration = audio_clip.duration + scene.pause
        
        # ═══════════════════════════════════════════════════════════════════
        # MULTI-ASSET SCENE SUPPORT
        # ═══════════════════════════════════════════════════════════════════
        scene_clips = []
        if scene.assets:
            n_assets = len(scene.assets)
            duration_per_asset = total_scene_duration / n_assets
            
            for asset_idx, asset in enumerate(scene.assets):
                asset_path = os.path.join(assets_dir, asset.type)
                
                if not os.path.exists(asset_path):
                    # Check for common extensions if not specified
                    found = False
                    for ext in ['.png', '.jpg', '.jpeg']:
                        if os.path.exists(asset_path + ext):
                            asset_path += ext
                            found = True
                            break
                    
                    if not found:
                        logger.log(f"  ⚠️ Asset no encontrado: {asset.type}")
                        # Black frame fallback
                        clip_item = ImageClip(np.zeros((target_size[1], target_size[0], 3), dtype=np.uint8), duration=duration_per_asset)
                        scene_clips.append(clip_item)
                        continue

                # Get overlay path if specified
                overlay_path = None
                if asset.overlay:
                    overlay_path = os.path.join(overlay_dir, f"{asset.overlay}.mp4")
                    if not os.path.exists(overlay_path):
                        overlay_path = None
                
                # Apply Ken Burns
                clip_item = apply_ken_burns(
                    asset_path,
                    duration_per_asset,
                    target_size,
                    zoom=asset.zoom or "1.0:1.0",
                    move=asset.move or "HOR:50:50",
                    overlay_path=overlay_path,
                    fit=asset.fit
                )
                scene_clips.append(clip_item)
        else:
            # No assets - black frame
            clip_item = ImageClip(np.zeros((target_size[1], target_size[0], 3), dtype=np.uint8), duration=total_scene_duration)
            scene_clips.append(clip_item)
        
        # Combine all assets in the scene
        if len(scene_clips) > 1:
            scene_video = concatenate_videoclips(scene_clips, method="chain")
        else:
            scene_video = scene_clips[0]
            
        # Set audio
        scene_video = scene_video.with_audio(audio_clip)
        clips.append(scene_video)
        
        current_time += total_scene_duration
        
        # Track Timestamps (Start Time of Scene)
        mins, secs = divmod(int(current_time - total_scene_duration), 60)
        timestamps_list.append(f"{mins:02d}:{secs:02d} - {scene.title}")
        
        logger.log(f"  ✅ Clip generado: {scene.title} ({total_scene_duration:.1f}s, {len(scene.assets)} assets)")
    
    # Concatenate all clips
    logger.log("🔗 Concatenando clips...")
    final_video = concatenate_videoclips(clips, method="compose")
    
    # ═══════════════════════════════════════════════════════════════════
    # MUSIC LAYERING IMPLEMENTATION
    # ═══════════════════════════════════════════════════════════════════
    from moviepy import afx
    
    bg_music_obj = project.background_music
    if bg_music_obj:
        try:
            logger.log(f"🎵 Agregando música de fondo: {bg_music_obj.name}")
            bg_music_path = bg_music_obj.file.path
            
            if os.path.exists(bg_music_path):
                bg_audio = AudioFileClip(bg_music_path)
                
                # Loop music to cover video duration
                loops = int(final_video.duration / bg_audio.duration) + 1
                bg_audio_looped = bg_audio.with_effects([afx.AudioLoop(n_loops=loops)]).with_duration(final_video.duration)
                
                # Set volume
                bg_audio_final = bg_audio_looped.with_effects([afx.MultiplyVolume(project.music_volume)])
                
                # Mix with original audio
                final_audio = CompositeAudioClip([final_video.audio, bg_audio_final])
                final_video = final_video.with_audio(final_audio)
        except Exception as e:
            logger.log(f"⚠️ Error al mezclar música: {e}")
    
    # Export
    output_path = os.path.join(settings.MEDIA_ROOT, 'videos', f'project_{project.id}.mp4')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    logger.log("💾 Exportando video...")
    final_video.write_videofile(
        output_path,
        fps=30,
        codec='libx264',
        audio_codec='aac',
        preset='medium',
        threads=4
    )
    
    # Update project
    project.output_video.name = f'videos/project_{project.id}.mp4'
    project.status = 'completed'
    
    # Save Timestamps (YouTube Chapters)
    if timestamps_list:
        project.timestamps = "\n".join(timestamps_list)
        
    project.save()
    
    elapsed = time.time() - start_time
    logger.log(f"✅ Video generado exitosamente en {int(elapsed)}s ({int(elapsed/60)}:{int(elapsed%60):02d})")
    
    # Cleanup temp audio
    logger.log("🧹 Limpiando archivos temporales de audio...")
    
    # Close clips first to release file locks (Critical on Windows)
    try:
        final_video.close()
        for clip in clips:
            clip.close()
            if clip.audio:
                clip.audio.close()
    except Exception as e:
        logger.log(f"⚠️ Error cerrando clips: {e}")

    # Delete files
    cleaned_count = 0
    for _, audio_path in audio_files:
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
                cleaned_count += 1
        except Exception as e:
            logger.log(f"⚠️ Error borrando {os.path.basename(audio_path)}: {e}")
            
    logger.log(f"✨ Se eliminaron {cleaned_count} archivos de audio temporales.")
    
    return output_path
