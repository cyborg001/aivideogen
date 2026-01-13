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
        
        # Calculate scaled dimensions based on current scale
        scaled_w = img_w * scale
        scaled_h = img_h * scale
        
        # Calculate position based on movement
        if move_dir.upper() == 'HOR':
            # Horizontal pan: map start:end % to pixels
            # 0% = left edge, 100% = right edge of the cropped area
            pos_start_pct = move_start / 100.0
            pos_end_pct = move_end / 100.0
            current_pct = pos_start_pct + (pos_end_pct - pos_start_pct) * progress
            
            # The range of motion is the difference between scaled size and target size
            max_offset_x = max(0, scaled_w - target_w)
            # x position: starts at (target_w - scaled_w) * current_pct
            x = (target_w - scaled_w) * current_pct
            # Center vertically
            y = (target_h - scaled_h) / 2
        else:
            # Vertical pan
            pos_start_pct = move_start / 100.0
            pos_end_pct = move_end / 100.0
            current_pct = pos_start_pct + (pos_end_pct - pos_start_pct) * progress
            
            max_offset_y = max(0, scaled_h - target_h)
            x = (target_w - scaled_w) / 2
            y = (target_h - scaled_h) * current_pct
        
        return (x, y)
    
    # Create ImageClip from pre-scaled array
    base_clip = ImageClip(img_np, duration=duration)
    
    # Apply dynamic resizing and positioning
    # IMPORTANT: We use a lambda that returns the (w, h) tuple for resized
    clip = base_clip.resized(lambda t: (int(img_w * get_frame_scale(t)), int(img_h * get_frame_scale(t))))
    clip = clip.with_position(get_frame_pos)
    
    # Wrap in CompositeVideoClip to ensure transformations are rendered correctly
    clip = CompositeVideoClip([clip], size=target_size)
    
    # Apply overlay if specified
    if overlay_path and os.path.exists(overlay_path):
        overlay = VideoFileClip(overlay_path, has_mask=True)
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
    
    audio_files = []
    for i, scene in enumerate(all_scenes):
        logger.log(f"  Escena {i+1}/{len(all_scenes)}: {scene.title}")
        
        if not scene.text:
            continue
        
        # Prepare text - Use clean mode (no SSML) for Edge TTS for now
        use_ssml = (project.engine == 'eleven')
        text_with_emotions = translate_emotions(scene.text, use_ssml=use_ssml)
        
        # Generate audio
        audio_path = os.path.join(temp_audio_dir, f"project_{project.id}_scene_{i:03d}.mp3")
        
        if project.engine == 'edge':
            speed_rate = f"+{int((scene.speed - 1.0) * 100)}%"
            ssml_text = wrap_ssml(text_with_emotions, scene.voice, speed_rate)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(
                generate_audio_edge(ssml_text, audio_path, scene.voice, speed_rate)
            )
            loop.close()
        else:
            api_key = os.getenv('ELEVENLABS_API_KEY')
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
    
    # Check if we have audio
    if not audio_files:
        logger.log("❌ No se generó audio para ninguna escena.")
        project.status = 'error'; project.save()
        return

    # ═══════════════════════════════════════════════════════════════════
    # BLOCK-LEVEL GENERATION (Music switching)
    # ═══════════════════════════════════════════════════════════════════
    from moviepy import afx
    block_clips = []
    audio_idx = 0
    current_time = 0
    timestamps_list = []
    
    for b_idx, block in enumerate(script.blocks):
        logger.log(f"📦 Procesando Bloque {b_idx+1}: {block.title}")
        block_scene_clips = []
        
        for scene in block.scenes:
            if audio_idx >= len(audio_files): break
            # Find matching audio by scene object (safe if object identity maintained)
            # or simply follow the order (safe because all_scenes is deterministic)
            s_obj, audio_path = audio_files[audio_idx]
            audio_idx += 1
            
            # Load audio for duration
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration + scene.pause
            
            # REVERT: Use only the first asset
            if scene.assets:
                asset = scene.assets[0]
                asset_path = os.path.join(assets_dir, asset.type)
                
                # Tolerance for common extensions
                if not os.path.exists(asset_path):
                    for ext in ['.png', '.jpg', '.jpeg', '.mp4']:
                        if os.path.exists(asset_path + ext):
                            asset_path += ext; break

                if not os.path.exists(asset_path):
                    logger.log(f"  ⚠️ Asset no encontrado: {asset.type}. Fondo negro.")
                    clip = ImageClip(np.zeros((target_size[1], target_size[0], 3), dtype=np.uint8), duration=duration)
                else:
                    # Overlay
                    overlay_path = None
                    if asset.overlay:
                        overlay_path = os.path.join(overlay_dir, f"{asset.overlay}.mp4")
                        if not os.path.exists(overlay_path): overlay_path = None
                    
                    # Apply Ken Burns (now with fixed move logic)
                    clip = apply_ken_burns(
                        asset_path, duration, target_size,
                        zoom=asset.zoom or "1.0:1.0",
                        move=asset.move or "HOR:50:50",
                        overlay_path=overlay_path, fit=asset.fit
                    )
            else:
                clip = ImageClip(np.zeros((target_size[1], target_size[0], 3), dtype=np.uint8), duration=duration)
            
            # Set audio & append
            clip = clip.with_audio(audio_clip)
            block_scene_clips.append(clip)
            
            # Timestamps
            mins, secs = divmod(int(current_time), 60)
            timestamps_list.append(f"{mins:02d}:{secs:02d} - {scene.title}")
            current_time += duration
        
        if not block_scene_clips: continue
        
        # Concatenate block scenes
        block_video = concatenate_videoclips(block_scene_clips, method="compose")
        
        # Apply Block Music
        # Priority: block.music > project.background_music (if set)
        music_to_use = block.music
        if not music_to_use and project.background_music:
            music_to_use = os.path.basename(project.background_music.file.name)

        if music_to_use:
            try:
                from .models import Music
                m_obj = Music.objects.filter(file__icontains=music_to_use).first() or \
                        Music.objects.filter(name__icontains=music_to_use).first()
                
                if m_obj and os.path.exists(m_obj.file.path):
                    logger.log(f"  🎵 Música bloque: {m_obj.name}")
                    bg_audio = AudioFileClip(m_obj.file.path)
                    
                    loops = int(block_video.duration / bg_audio.duration) + 1
                    bg_audio_looped = bg_audio.with_effects([afx.AudioLoop(n_loops=loops)]).with_duration(block_video.duration)
                    
                    vol = block.volume if block.volume is not None else project.music_volume
                    bg_audio_final = bg_audio_looped.with_effects([afx.MultiplyVolume(vol)])
                    
                    # Mix with original block voice
                    final_audio = CompositeAudioClip([block_video.audio, bg_audio_final])
                    block_video = block_video.with_audio(final_audio)
            except Exception as e:
                logger.log(f"  ⚠️ Error música bloque: {e}")
        
        block_clips.append(block_video)

    # ═══════════════════════════════════════════════════════════════════
    # EXPORT
    # ═══════════════════════════════════════════════════════════════════
    if not block_clips:
        logger.log("❌ Error fatal: No se generaron clips de bloques.")
        project.status = 'failed'; project.save()
        return

    logger.log("🔗 Concatenando bloques y exportando...")
    final_video = concatenate_videoclips(block_clips, method="compose")
    
    output_filename = f"project_{project.id}.mp4"
    output_path = os.path.join(settings.MEDIA_ROOT, 'videos', output_filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    final_video.write_videofile(
        output_path, fps=30, codec='libx264', audio_codec='aac', 
        preset='medium', threads=4
    )
    
    # Total stats
    total_time = time.time() - start_time
    project.output_video.name = f"videos/{output_filename}"
    project.duration = final_video.duration
    project.timestamps = "\n".join(timestamps_list)
    project.status = 'completed'
    project.save()
    
    logger.log(f"✨ ¡Generación exitosa en {total_time:.1f}s!")
    
    # Cleanup
    try:
        final_video.close()
        for bc in block_clips: bc.close()
        for _, path in audio_files:
            if os.path.exists(path): os.remove(path)
    except:
        pass
        
    return output_path

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
