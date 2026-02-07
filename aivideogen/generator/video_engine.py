"""
AVGL v4.0 - Video Generation Engine
Handles the complete video rendering pipeline with optimizations
"""

import os
import time
import re
import numpy as np
import logging
from django.conf import settings

# v8.5 Notification Support
if os.name == 'nt':
    try:
        import winsound
    except ImportError:
        winsound = None
else:
    winsound = None

logger = logging.getLogger(__name__)

def play_finish_sound(success=True):
    """Plays a system sound to notify the user that rendering has finished."""
    if winsound:
        try:
            if success:
                # MB_ICONASTERISK (64) - Standard success/info sound
                winsound.MessageBeep(64)
            else:
                # MB_ICONHAND (16) - Standard error sound
                winsound.MessageBeep(16)
        except Exception as e:
            print(f"Error playing notification sound: {e}")


# ═══════════════════════════════════════════════════════════════════
# Ken Burns Effect (Optimized with Pre-Scaling)
# ═══════════════════════════════════════════════════════════════════

def apply_ken_burns(image_path, duration, target_size, zoom="1.0:1.3", move="HOR:50:50", overlay_path=None, fit=None, shake=False, rotate=None, shake_intensity=5, w_rotate=None):
    """
    Applies optimized Ken Burns effect with robust sizing and movement.
    Supports diagonal movement: "HOR:start:end + VER:start:end"
    v11.8: Added SHAKE and ROTATE support.
    """
    from moviepy import ImageClip, VideoFileClip, CompositeVideoClip, vfx
    from PIL import Image
    
    # ═══════════════════════════════════════════════════════════════════
    # 1. PARSE PARAMETERS
    # ═══════════════════════════════════════════════════════════════════
    # Expected format: "X:Y" (e.g. "1.0:1.3") or "X" (e.g. "1.5")
    z_start, z_end = 1.0, 1.0
    if zoom:
        if isinstance(zoom, str) and ':' in zoom:
            z_parts = zoom.split(':')
            z_start = float(z_parts[0])
            z_end = float(z_parts[1]) if len(z_parts) > 1 else z_start
        else:
            try:
                z_start = float(zoom)
                z_end = z_start
            except: pass
    
    # ═══════════════════════════════════════════════════════════════════
    # DIAGONAL SUPPORT (HOR:start:end + VER:start:end)
    # ═══════════════════════════════════════════════════════════════════
    move_configs = []
    if move and '+' in move:
        # Combined move: "HOR:0:100 + VER:50:50"
        parts = [p.strip() for p in move.split('+')]
        for p in parts:
            mp = p.split(':')
            mdir = mp[0].upper()
            mstart = float(mp[1]) if len(mp) > 1 else 50.0
            mend = float(mp[2]) if len(mp) > 2 else mstart
            move_configs.append({'dir': mdir, 'start': mstart, 'end': mend})
    else:
        # Single move or default
        m_parts = move.split(':') if move else ['HOR', '50', '50']
        m_dir = m_parts[0].upper() if len(m_parts) > 0 else 'HOR'
        m_start = float(m_parts[1]) if len(m_parts) > 1 else 50.0
        m_end = float(m_parts[2]) if len(m_parts) > 2 else m_start
        move_configs.append({'dir': m_dir, 'start': m_start, 'end': m_end})

    # ═══════════════════════════════════════════════════════════════════
    # 2. LOAD & BASE SCALING
    # ═══════════════════════════════════════════════════════════════════
    img = Image.open(image_path).convert("RGB")
    w_orig, h_orig = img.size
    target_w, target_h = target_size
    
    # Decide Base Scale: FIT (Contain) vs COVER
    scale_w = target_w / w_orig
    scale_h = target_h / h_orig
    
    is_fit = (fit == "contain" or fit is True)
    if is_fit:
        base_scale = min(scale_w, scale_h)
    else:
        base_scale = max(scale_w, scale_h)
    
    # Smart Slack: Add 15% buffer if moving on a constrained axis
    if not is_fit:
        has_hor = any(c['dir'] == 'HOR' for c in move_configs)
        has_ver = any(c['dir'] == 'VER' for c in move_configs)
        if has_hor and scale_w >= (base_scale * 0.99): base_scale *= 1.15
        if has_ver and scale_h >= (base_scale * 0.99): base_scale *= 1.15

    # OPTIMIZATION: Work with pre-scaled image
    working_scale = base_scale * max(z_start, z_end)
    working_img = img.resize((int(w_orig * working_scale), int(h_orig * working_scale)), Image.Resampling.BICUBIC)
    img_np = np.array(working_img)
    working_h, working_w = img_np.shape[:2]

    def get_frame_scale(t):
        progress = (t / duration) if duration > 0 else 1.0
        rel_zoom = z_start + (z_end - z_start) * progress
        return rel_zoom / max(z_start, z_end)

    def get_frame_pos(t):
        progress = (t / duration) if duration > 0 else 1.0
        scale = get_frame_scale(t)
        curr_w = working_w * scale; curr_h = working_h * scale
        slack_x = curr_w - target_w; slack_y = curr_h - target_h
        
        # Default Centered
        x = (target_w - curr_w) / 2
        y = (target_h - curr_h) / 2

        for cfg in move_configs:
            p_prog = cfg['start'] + (cfg['end'] - cfg['start']) * progress
            if cfg['dir'] == 'HOR':
                x = -(p_prog / 100.0) * slack_x
            elif cfg['dir'] == 'VER':
                y = -((100.0 - p_prog) / 100.0) * slack_y
        
        # ═══════════════════════════════════════════════════════════════════
        # SHAKE EFFECT (v12.1 Parametric)
        # ═══════════════════════════════════════════════════════════════════
        if shake:
            shake_freq = 12.0 # Hz
            # v12.1: Use intensity from JSON or default to 5. Pixels = intensity * 1.5
            intensity = float(shake_intensity if shake_intensity else 5)
            shake_amp = intensity * 1.6   # 5 * 1.6 = 8px (v11 legacy)
            
            x += np.sin(t * shake_freq * 2 * np.pi) * shake_amp * np.random.uniform(0.5, 1.0)
            y += np.cos(t * shake_freq * 1.5 * np.pi) * shake_amp * np.random.uniform(0.5, 1.0)

        return (x, y)

    base_clip = ImageClip(img_np, duration=duration)
    clip = base_clip.resized(get_frame_scale).with_position(get_frame_pos)

    # ═══════════════════════════════════════════════════════════════════
    # ROTATE EFFECT (v11.8)
    # ═══════════════════════════════════════════════════════════════════
    if rotate:
        try:
            r_start, r_end = 0.0, 0.0
            if isinstance(rotate, str) and ':' in rotate:
                r_parts = rotate.split(':')
                r_start = float(r_parts[0])
                r_end = float(r_parts[1])
            else:
                r_start = float(rotate)
                r_end = r_start
            
            # v12.3: 1 value = static, range = animated
            if r_start == r_end:
                # v12.5 Fix: expand=False prevents center wobble
                clip = clip.rotated(r_start, resample="bicubic", expand=False)
            else:
                # Dynamic Rotation over duration
                def get_rot(t): 
                    # v12.4: Fixed Angular Velocity (deg/s) if w_rotate is present
                    if w_rotate is not None:
                        try:
                            w_val = float(w_rotate)
                            return r_start + w_val * t
                        except: pass

                    # Default: Interpolate relative to duration
                    prog = (t / duration) if duration > 0 else 1.0
                    return r_start + (r_end - r_start) * prog
                
                # v12.5 Fix: expand=False to fix wobble
                clip = clip.with_effects([vfx.Rotate(get_rot, resample="bicubic", expand=False)])
        except Exception as e:
            logger.warning(f"Error applying rotation '{rotate}': {e}")
    
    if not overlay_path or not os.path.exists(overlay_path):
        # v8.6.1: Must ALWAYS return CompositeVideoClip to enforce target_size
        # Returning 'clip' directly was causing odd dimensions (Encoder Error)
        return CompositeVideoClip([clip.with_duration(duration)], size=target_size, bg_color=(0,0,0)).with_duration(duration)
    
    # ═══════════════════════════════════════════════════════════════════
    # 3. OVERLAY PROCESSING (Only if needed)
    # ═══════════════════════════════════════════════════════════════════
    overlay = VideoFileClip(overlay_path, has_mask=True)
    if overlay.duration < duration:
        overlay = overlay.with_effects([vfx.Loop(duration=duration)])
    overlay = overlay.resized(target_size).subclipped(0, duration)
    overlay = overlay.with_mask(overlay.to_mask()).with_opacity(0.4).without_audio()
    
    return CompositeVideoClip([clip, overlay], size=target_size, bg_color=(0,0,0)).with_duration(duration)


def process_video_asset(video_path, duration, target_size, overlay_path=None, fit=None, clips_to_close=None):
    """
    Processes a video asset to fit the scene: looping, trimming, and scaling.
    """
    from moviepy import VideoFileClip, CompositeVideoClip, vfx
    
    # Load video
    v_clip = VideoFileClip(video_path)
    if clips_to_close is not None: clips_to_close.append(v_clip)
    
    # Handle duration: Loop if shorter than scene
    if v_clip.duration < duration:
        v_clip = v_clip.with_effects([vfx.Loop(duration=duration)])
    
    # Trim to scene duration
    v_clip = v_clip.subclipped(0, duration)
    
    # Scaling logic (Contain vs Cover)
    w_orig, h_orig = v_clip.size
    target_w, target_h = target_size
    
    scale_w = target_w / w_orig
    scale_h = target_h / h_orig
    
    is_fit = (fit == "contain" or fit is True)
    if is_fit:
        base_scale = min(scale_w, scale_h)
    else:
        base_scale = max(scale_w, scale_h)
        
    v_clip = v_clip.resized(base_scale)
    
    # Position centered
    v_clip = v_clip.with_position("center")
    
    layers = [v_clip]
    
    # Overlay support for video assets too
    if overlay_path and os.path.exists(overlay_path):
        overlay = VideoFileClip(overlay_path, has_mask=True)
        if clips_to_close is not None: clips_to_close.append(overlay)
        if overlay.duration < duration:
            overlay = overlay.with_effects([vfx.Loop(duration=duration)])
        overlay = overlay.resized(target_size).subclipped(0, duration)
        overlay = overlay.with_mask(overlay.to_mask()).with_opacity(0.4).without_audio()
        layers.append(overlay)
        
    return CompositeVideoClip(layers, size=target_size, bg_color=(0,0,0)).with_duration(duration)


# ═══════════════════════════════════════════════════════════════════
# Main Video Generation Function
# ═══════════════════════════════════════════════════════════════════

def generate_video_avgl(project):
    """
    Main video generation function using AVGL v4.0 JSON format.
    v8.6.2: Wrapped in Global Error Listener for robust notifications.
    """
    from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, VideoFileClip, CompositeAudioClip, CompositeVideoClip, vfx
    from .avgl_engine import parse_avgl_json, translate_emotions, wrap_ssml, generate_audio_edge, generate_audio_elevenlabs
    from .utils import ProjectLogger
    import asyncio
    import numpy as np
    from moviepy import AudioClip, ColorClip, afx, TextClip
    from .models import Music
    from django.db.models import Q
    
    start_time = time.time()
    logger = ProjectLogger(project)
    
    # Init Progress
    project.progress = 5
    project.save(update_fields=['progress'])
    
    try:
        audio_files = []
        block_clips = []
        # v9.6: Tracking for all clips to ensure proper closure (Windows WinError 32 mitigation)
        clips_to_close = []
        
        # Prepare
        project.status = 'processing'
        project.save()
        
        # Log Video Format
        format_type = "SHORT" if project.aspect_ratio == 'portrait' else "VIDEO"
        logger.log(f"[Engine] Iniciando v8.6.2 | FORMATO: {format_type}")
        
        # 1. Parse script
        try:
            script_text = project.script_text
            script = parse_avgl_json(script_text)
            logger.log(f"[OK] Script parseado: '{script.title}'")
        except Exception as e:
            logger.log(f"[Error] Error al parsear JSON: {e}")
            project.status = 'error'; project.save()
            play_finish_sound(success=False)
            return

        # Update project title if specified and NOT already set by user manually
        if script.title and project.title in ["Sin Título", "Video Sin Título", "Proyecto sin título", ""]:
            project.title = script.title; project.save()

        # FORCE OVERRIDE: Apply Project Voice to Script
        if project.voice_id:
            script.voice = project.voice_id
            for block in script.blocks:
                for scene in block.scenes:
                    if not scene.voice or scene.voice == "es-ES-AlvaroNeural":
                        scene.voice = project.voice_id
        
        # Setup directories
        temp_audio_dir = os.path.join(settings.MEDIA_ROOT, 'temp_audio')
        os.makedirs(temp_audio_dir, exist_ok=True)
        assets_dir = os.path.join(settings.MEDIA_ROOT, 'assets')
        overlay_dir = os.path.join(settings.MEDIA_ROOT, 'overlays')
        
        # Target resolution (Ensuring even numbers for H.264 compatibility)
        target_size = (1080, 1920) if project.aspect_ratio == 'portrait' else (1920, 1080)
        target_size = ((target_size[0] // 2) * 2, (target_size[1] // 2) * 2)
        
        # 2. Generate audio for all scenes
        logger.log("[Audio] Generando segmentos...")
        all_scenes = script.get_all_scenes()
        
        # v5.2.1: Pre-calculate durations for Master Shot interpolation
        audio_durations = {}
        for i, scene in enumerate(all_scenes):
            logger.log(f"  Escena {i+1}/{len(all_scenes)}: {scene.title}")
            
            audio_path = os.path.join(temp_audio_dir, f"project_{project.id}_scene_{i:03d}.mp3")
            
            # Custom Audio Priority
            if scene.audio:
                custom_audio_path = os.path.join(assets_dir, scene.audio)
                if not os.path.exists(custom_audio_path): custom_audio_path = os.path.join(settings.MEDIA_ROOT, scene.audio)
                if os.path.exists(custom_audio_path):
                    logger.log(f"    🔊 Usando audio personalizado: {os.path.basename(custom_audio_path)}")
                    import shutil; shutil.copy2(custom_audio_path, audio_path)
                    audio_files.append((scene, audio_path))
                    try: temp_clip = AudioFileClip(audio_path); audio_durations[scene] = temp_clip.duration; temp_clip.close()
                    except: audio_durations[scene] = 1.0
                    continue

            if not scene.text:
                audio_files.append((scene, None)); audio_durations[scene] = 1.0; continue
                
            use_ssml = (project.engine == 'eleven')
            curr_text = re.sub(r'\(.*?\)', '', scene.text).strip()
            if curr_text.startswith('[') and not re.match(r'^\[\s*SUB', curr_text, flags=re.IGNORECASE):
                curr_text = re.sub(r'^\[(?!(?:\s*/?SUB|TENSO|EPICO|SUSPENSO|GRITANDO|SUSURRO))[^\]]+\]\s*', '', curr_text, flags=re.IGNORECASE)

            text_with_emotions = translate_emotions(curr_text, use_ssml=use_ssml)
            
            success = False
            if project.engine == 'edge':
                env_rate = os.getenv("EDGE_TTS_RATE", "+0%")
                speed_rate = f"+{int((scene.speed - 1.0) * 100)}%" if scene.speed != 1.0 else env_rate
                loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
                success = loop.run_until_complete(generate_audio_edge(text_with_emotions, audio_path, scene.voice, speed_rate, pitch=scene.pitch or "+0Hz", scene=scene))
                loop.close()
            else:
                api_key = os.getenv('ELEVENLABS_API_KEY')
                voice_id = os.getenv('ELEVENLABS_VOICE_ID', 'EXAVITQu4vr4xnSDxMaL')
                success = asyncio.run(generate_audio_elevenlabs(text_with_emotions, audio_path, voice_id, api_key))
            
            if success:
                audio_files.append((scene, audio_path))
                try: temp_clip = AudioFileClip(audio_path); audio_durations[scene] = temp_clip.duration; temp_clip.close()
                except: audio_durations[scene] = 1.0
            else:
                logger.log(f"  ⚠️ Error generando audio para escena {i+1}")
                audio_files.append((scene, None))
                audio_durations[scene] = 1.0

        # Check if we have at least some audio or scenes
        if not audio_files:
            logger.log("❌ Error fatal: No se generó ningún audio.")
            project.status = 'error'; project.save()
            play_finish_sound(success=False)
            return
            
        # Progress: Audio Generated
        project.progress = 35
        project.save(update_fields=['progress'])

        # 3. Main Clip Generation Loop
        logger.log("[Video] Procesando escenas...")
        block_metadata = []
        current_time = 0.0
        timestamps_list = []
        
        # Create a Scene-to-Audio mapping to prevent desync
        scene_audio_map = {scene: audio for scene, audio in audio_files}

        for b_idx, block in enumerate(script.blocks):
            # Calculate Progress (35% to 85%)
            # Based on block index
            total_blocks = len(script.blocks)
            if total_blocks > 0:
                p_increment = 50 / total_blocks
                current_p = 35 + (b_idx * p_increment)
                project.progress = int(current_p)
                project.save(update_fields=['progress'])

            logger.log(f"📦 Procesando Bloque {b_idx+1}: {block.title}")
            block_scene_clips = []
            block_voice_intervals = []
            block_cursor = 0.0
            
            for s_idx, scene in enumerate(block.scenes):
                # 1. Audio Retrieval (Robust)
                audio_clip = None
                voice_duration = 0.0
                if scene in scene_audio_map and scene_audio_map[scene]:
                    audio_path = scene_audio_map[scene]
                    audio_clip = AudioFileClip(audio_path)
                    clips_to_close.append(audio_clip)
                    voice_duration = audio_clip.duration
                
                # Fallback for missing audio (ensures sync)
                if not audio_clip:
                    logger.log(f"  ⚠️ Audio NO generado per escena {s_idx+1}. Usando silencio.")
                    audio_clip = AudioClip(lambda t: [0,0], duration=1.0)
                
                duration = audio_clip.duration + scene.pause
                
                # ASSET LOADING & FALLBACK
                clip = None
                if scene.assets:
                    asset = scene.assets[0]
                    asset_path = os.path.join(assets_dir, asset.type)
                    if not os.path.exists(asset_path):
                        for ext in ['.png', '.jpg', '.jpeg', '.mp4']:
                            if os.path.exists(asset_path + ext): asset_path += ext; break

                    if not os.path.exists(asset_path):
                        logger.log(f"  ⚠️ Asset no encontrado: {asset.type}. Buscando respaldo...")
                        # Smart Fallback
                        fallback_candidates = [os.path.join(assets_dir, "notiaci_intro_wide.png"), os.path.join(assets_dir, "banner_notiaci.png")]
                        found_fb = False
                        for fb in fallback_candidates:
                            if os.path.exists(fb): asset_path = fb; found_fb = True; break
                        if not found_fb:
                            try:
                                any_imgs = [f for f in os.listdir(assets_dir) if f.lower().endswith(('.png', '.jpg'))]
                                if any_imgs: asset_path = os.path.join(assets_dir, any_imgs[0]); found_fb = True
                            except: pass
                        
                        if not found_fb:
                            clip = ColorClip(size=target_size, color=(0,0,0), duration=duration)
                            logger.log("  🛑 No hay assets disponibles. Usando fondo negro.")
                        else:
                            clip = apply_ken_burns(asset_path, duration, target_size, zoom="1.1:1.0", move="HOR:50:50")
                            logger.log(f"  💡 Respaldo encontrado: {os.path.basename(asset_path)}")
                    
                    if not clip and os.path.exists(asset_path):
                        # ═══════════════════════════════════════════════════════════════════
                        # MASTER SHOT / GROUP INTERPOLATION (v5.2)
                        eff_zoom = asset.zoom or "1.0:1.3"
                        eff_move = asset.move or "HOR:50:50"
                        
                        if scene.group_id and scene.group_settings:
                            g = scene.group_settings
                            g_zoom = g.get("zoom", "1.0:1.3")
                            g_move = g.get("move", "HOR:50:50")
                            
                            # Calculate group timing
                            group_scenes = [s for s in all_scenes if s.group_id == scene.group_id]
                            total_group_duration = sum([audio_durations.get(s, 1.0) + s.pause for s in group_scenes])
                            
                            # Find start time of CURRENT scene relative to group start
                            start_in_group = 0.0
                            for s in group_scenes:
                                if s == scene: break
                                s_dur = audio_durations.get(s, 1.0) + s.pause
                                start_in_group += s_dur
                            
                            # Interpolate Zoom
                            z_parts = g_zoom.split(':') if ':' in g_zoom else [g_zoom, g_zoom]
                            gz_start = float(z_parts[0]); gz_end = float(z_parts[1])
                            
                            z_s = gz_start + (gz_end - gz_start) * (start_in_group / total_group_duration)
                            z_e = gz_start + (gz_end - gz_start) * ((start_in_group + duration) / total_group_duration)
                            eff_zoom = f"{z_s:.3f}:{z_e:.3f}"
                            
                            # Interpolate Move (Simple Linear)
                            # We handle HOR:start:end
                            # v9.6 Fix: Support for combined moves in group-scene interpolation
                            m_configs = []
                            if '+' in g_move:
                                for p in [p.strip() for p in g_move.split('+')]:
                                    mp = p.split(':')
                                    if len(mp) >= 3: m_configs.append({'dir': mp[0], 's': float(mp[1]), 'e': float(mp[2])})
                            else:
                                mp = g_move.split(':')
                                if len(mp) >= 3: m_configs.append({'dir': mp[0], 's': float(mp[1]), 'e': float(mp[2])})
                            
                            for cfg in m_configs:
                                ms = cfg['s']; me = cfg['e']
                                m_s = ms + (me - ms) * (start_in_group / total_group_duration)
                                m_e = ms + (me - ms) * ((start_in_group + duration) / total_group_duration)
                                if cfg['dir'] == 'HOR':
                                    eff_move = f"HOR:{m_s:.1f}:{m_e:.1f}" if not eff_move or '+' not in eff_move else eff_move + f" + HOR:{m_s:.1f}:{m_e:.1f}"
                                else:
                                    eff_move += f" + VER:{m_s:.1f}:{m_e:.1f}" if eff_move else f"VER:{m_s:.1f}:{m_e:.1f}"

                        logger.log(f"  🎬 Escena {s_idx+1}: {os.path.basename(asset_path)} | Zoom: {eff_zoom} | Move: {eff_move}")
                        
                        # Overlay
                        overlay_path = None
                        if asset.overlay:
                            overlay_path = os.path.join(overlay_dir, f"{asset.overlay}.mp4")
                            if not os.path.exists(overlay_path): overlay_path = None
                        
                        # Determine Asset Type (Image vs Video)
                        is_video = asset_path.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))
                        
                        if is_video:
                            logger.log(f"  📽️ Asset detectado como VÍDEO: {os.path.basename(asset_path)}")
                            clip = process_video_asset(
                                asset_path, duration, target_size,
                                overlay_path=overlay_path,
                                fit=asset.fit,
                                clips_to_close=clips_to_close
                            )
                        else:
                            # Apply Ken Burns (Standard image logic)
                            clip = apply_ken_burns(
                                asset_path, duration, target_size,
                                zoom=eff_zoom,
                                move=eff_move,
                                overlay_path=overlay_path, 
                                fit=asset.fit,
                                shake=getattr(asset, 'shake', False),
                                shake_intensity=getattr(asset, 'shake_intensity', 5),
                                rotate=getattr(asset, 'rotate', None),
                                w_rotate=getattr(asset, 'w_rotate', None)
                            )
                else:
                    # v8.6: FAST AUDIO TEST MODE
                    # Use ColorClip for maximum speed when user explicitly omits assets (for audio testing)
                    logger.log(f"  🔇 Modo Solo Audio/Debug: Sin assets. Fondo negro rápido.")
                    clip = ColorClip(size=target_size, color=(0,0,0), duration=duration)

                # 2. SFX Processing (New)
                scene_sfx_clips = []
                if scene.sfx:
                    sfx_dir = os.path.join(settings.MEDIA_ROOT, 'sfx')
                    for sfx_item in scene.sfx:
                        sfx_path = os.path.join(sfx_dir, sfx_item.type)
                        # Tolerance for extension
                        if not os.path.exists(sfx_path):
                            for ext in ['.mp3', '.wav', '.m4a']:
                                if os.path.exists(sfx_path + ext):
                                    sfx_path += ext; break
                        
                        if os.path.exists(sfx_path):
                            try:
                                s_clip = AudioFileClip(sfx_path).with_effects([afx.MultiplyVolume(sfx_item.volume)])
                                if clips_to_close is not None: clips_to_close.append(s_clip)
                                
                                # AVGL v4: Offset is word-based. 
                                # Calculate delay: (scene_audio_duration / scene_word_count) * offset
                                delay = 0
                                if sfx_item.offset > 0 and audio_clip:
                                    # Count words in scene text
                                    clean_text = re.sub(r'\[.*?\]', '', scene.text)
                                    words = clean_text.split()
                                    if words:
                                        delay = (audio_clip.duration / len(words)) * sfx_item.offset
                                
                                scene_sfx_clips.append(s_clip.with_start(delay).with_duration(min(s_clip.duration, duration - delay)))
                                logger.log(f"    🔊 SFX: {os.path.basename(sfx_path)} (vol: {sfx_item.volume}, offset: {sfx_item.offset} words -> {delay:.2f}s)")
                            except Exception as e:
                                logger.log(f"    ⚠️ Error SFX {sfx_item.type}: {e}")

                # Mix Scene Audio (Voice + SFX)
                if scene_sfx_clips:
                    final_scene_audio = CompositeAudioClip([audio_clip] + scene_sfx_clips)
                    audio_clip = final_scene_audio

                # SUBTITLE RENDERING (Enhanced v6.2)
                # Priority: scene.subtitles (list from tags) > scene.subtitle (single string)
                sub_clips_dynamic = []
                try:
                    # Common Font detection
                    try:
                        font_list = TextClip.list('font')
                        font = 'Arial-Bold' if 'Arial-Bold' in font_list else 'C:/Windows/Fonts/arial.ttf'
                    except:
                        font = 'C:/Windows/Fonts/arial.ttf'
                    
                    fontsize = int(target_size[1] * 0.035)
                    
                    if hasattr(scene, 'subtitles') and scene.subtitles:
                        # v6.8: Use the same splitting logic for consistency
                        clean_text_for_count = scene.text
                        words_in_scene = clean_text_for_count.split()
                        total_words_scene = len(words_in_scene)
                        timing_base = voice_duration if voice_duration > 0 else duration
                        
                        logger.log(f"[Subs] Renderizando {len(scene.subtitles)} subtitulos de enfasis. Palabras totales: {total_words_scene}")
                        
                        for idx, sub_data in enumerate(scene.subtitles):
                            s_text = sub_data.get('text', '')
                            s_offset = sub_data.get('offset', 0)
                            s_w_count = sub_data.get('word_count', 4)
                            
                            if not s_text: continue
                            
                            # Estimate timing
                            s_start = (s_offset / total_words_scene) * timing_base if total_words_scene > 0 else 0
                            s_dur = (s_w_count / total_words_scene) * timing_base if total_words_scene > 0 else 2.5
                            
                            # Sanitize
                            s_start = min(s_start, duration - 0.1)
                            s_dur = min(s_dur, duration - s_start)
                            if s_dur < 0.4: s_dur = 0.5
                            
                            logger.log(f"       [{idx+1}] '{s_text[:20]}...' @ {s_start:.2f}s (dur: {s_dur:.2f}s, offset: {s_offset})")
                            
                            # v7.2: Fixed height for the black bar ensures perfect vertical centering
                            # Font size is reduced, but the bar height is generous (2.8x font size)
                            box_height = int(fontsize * 2.8)
                            
                            d_txt_clip = TextClip(
                                text=s_text,
                                font_size=fontsize,
                                color='yellow',
                                bg_color='black',
                                font=font,
                                method='caption',
                                text_align='center',
                                horizontal_align='center',
                                vertical_align='center',
                                size=(int(target_size[0]*0.85), box_height)
                            ).with_start(s_start).with_duration(s_dur)
                            
                            # Only adding horizontal margins for that "wide" look, vertical is handled by box_height
                            d_txt_clip = d_txt_clip.with_effects([vfx.Margin(left=30, right=30, color=(0,0,0))])
                            d_txt_clip = d_txt_clip.with_position(('center', 0.85), relative=True)
                            
                            sub_clips_dynamic.append(d_txt_clip)
                        
                        if sub_clips_dynamic:
                            clip = CompositeVideoClip([clip] + sub_clips_dynamic)
                            logger.log(f"    [OK] Desplegados {len(sub_clips_dynamic)} subtitulos en escena.")
                        
                except Exception as e:
                    logger.log(f"    [WARNING] Error renderizando subtitulos: {e}")

                # Set audio & append
                clip = clip.with_audio(audio_clip)
                block_scene_clips.append(clip)
                
                # Timestamps
                m, s = divmod(int(current_time), 60)
                timestamps_list.append(f"{m:02d}:{s:02d} {scene.title}")
                
                # Ducking Intervals
                if hasattr(scene, 'voice_intervals') and scene.voice_intervals:
                    for vs, ve in scene.voice_intervals: block_voice_intervals.append((block_cursor + vs, block_cursor + ve))
                else: block_voice_intervals.append((block_cursor, block_cursor + voice_duration))
                
                current_time += duration; block_cursor += duration

            if block_scene_clips:
                block_video = concatenate_videoclips(block_scene_clips, method="chain")
                
                # Apply Block Music (Local Ducking)
                music_to_use = block.music
                has_local_music = False
                
                if music_to_use:
                    try:
                        m_obj = Music.objects.filter(file__icontains=music_to_use).first() or \
                                Music.objects.filter(name__icontains=music_to_use).first()
                        
                        if m_obj and os.path.exists(m_obj.file.path):
                            has_local_music = True
                            logger.log(f"  [Audio] Musica especifica bloque: {m_obj.name}")
                            bg_audio = AudioFileClip(m_obj.file.path)
                            clips_to_close.append(bg_audio)
                        elif music_to_use and os.path.exists(music_to_use):
                            # v9.2: Direct path fallback for blocks
                            has_local_music = True
                            logger.log(f"  [Audio] Musica especifica bloque (directa): {os.path.basename(music_to_use)}")
                            bg_audio = AudioFileClip(music_to_use)
                            clips_to_close.append(bg_audio)
                        elif music_to_use:
                             # Try media-relative
                             potential_path = os.path.join(settings.MEDIA_ROOT, music_to_use)
                             if os.path.exists(potential_path):
                                 has_local_music = True
                                 logger.log(f"  [Audio] Musica especifica bloque (media): {os.path.basename(music_to_use)}")
                                 bg_audio = AudioFileClip(potential_path)
                                 clips_to_close.append(bg_audio)

                        if has_local_music:
                            loops = int(block_video.duration / bg_audio.duration) + 1
                            bg_audio_looped = bg_audio.with_effects([afx.AudioLoop(n_loops=loops)]).with_duration(block_video.duration)
                            
                            try:
                                peak_vol = float(block.volume) if block.volume is not None else float(script.music_volume)
                            except:
                                peak_vol = 0.2
                            
                            if peak_vol <= 0: peak_vol = 0.2
                            
                            duck_ratio = float(settings.AUDIO_DUCKING_RATIO)
                            at = float(settings.AUDIO_ATTACK_TIME)
                            rt = float(settings.AUDIO_RELEASE_TIME)

                            def volume_ducking_local(t):
                                # v9.3 Robust Local Ducking
                                if isinstance(t, np.ndarray):
                                    factors = np.ones_like(t, dtype=float)
                                    for start, end in block_voice_intervals:
                                        # Ducking
                                        factors[(t >= (start - at)) & (t <= (end + rt))] = duck_ratio
                                        # Fades
                                        m_out = (t >= (start - at)) & (t < start)
                                        if np.any(m_out):
                                            p = (t[m_out] - (start - at)) / at
                                            factors[m_out] = 1.0 - (p * (1.0 - duck_ratio))
                                        m_in = (t > end) & (t <= (end + rt))
                                        if np.any(m_in):
                                            p = (t[m_in] - end) / rt
                                            factors[m_in] = duck_ratio + (p * (1.0 - duck_ratio))
                                    return (float(peak_vol) * factors)[:, None]
                                else:
                                    factor = 1.0
                                    for start, end in block_voice_intervals:
                                        if start <= t <= end: factor = duck_ratio; break
                                        elif (start - at) <= t < start:
                                            p = (t - (start - at)) / at
                                            factor = 1.0 - (p * (1.0 - duck_ratio))
                                        elif end < t <= (end + rt):
                                            p = (t - end) / rt
                                            factor = duck_ratio + (p * (1.0 - duck_ratio))
                                    return float(peak_vol * factor)

                            bg_audio_final = bg_audio_looped.transform(lambda get_f, t: get_f(t) * volume_ducking_local(t))
                            final_audio = CompositeAudioClip([block_video.audio, bg_audio_final])
                            block_video = block_video.with_audio(final_audio)
                    except Exception as e:
                        logger.log(f"  ⚠️ Error música bloque: {e}")

                # Store metadata for Global Music Pass
                # v8.7: Music Volume Lock Logic
                if script.music_volume_lock and not has_local_music:
                    # If locked and no local music, force project/script global volume
                    bs_vol = script.music_volume if script.music_volume is not None else (project.music_volume if project.music_volume is not None else 0.18)
                else:
                    bs_vol = block.volume if block.volume is not None else (script.music_volume if script.music_volume is not None else 0.18)
                block_metadata.append({
                    'duration': block_video.duration,
                    'voice_intervals': block_voice_intervals, # Current Relative
                    'has_local_music': has_local_music,
                    'volume': bs_vol
                })
                block_clips.append(block_video)

        if not block_clips: raise Exception("No block clips generated")

        # 4. Final Export
        final_video = concatenate_videoclips(block_clips, method="chain")
        
        # ═══════════════════════════════════════════════════════════════════
        # GLOBAL MUSIC PROCESSING (Continuous)
        # ═══════════════════════════════════════════════════════════════════
        try:
            # 1. Determine Global Music Source
            # Priority: UI (Project) > Script JSON
            global_music_name = None
            if project.background_music:
                try: global_music_name = os.path.basename(project.background_music.file.name)
                except: pass
                
            if not global_music_name:
                global_music_name = script.background_music
                
            if global_music_name:
                logger.log(f"🔎 Buscando Música Global: {global_music_name}")
                # v5.2: SUPER ROBUST FUZZY LOOKUP
                
                # Normalize Search Term
                search_name = os.path.basename(global_music_name).lower()
                name_no_ext = re.sub(r'\.(mp3|wav|m4a)$', '', search_name)
                name_clean = name_no_ext.replace('_', ' ').replace('-', ' ').strip()
                name_slug = name_no_ext.replace(' ', '_').replace('-', '_').strip()
                
                # Search variations
                gm_obj = Music.objects.filter(
                    Q(file__icontains=name_no_ext) | 
                    Q(file__icontains=name_slug) | 
                    Q(name__icontains=name_clean) |
                    Q(name__icontains=name_no_ext)
                ).first()
                
                if gm_obj and os.path.exists(gm_obj.file.path):
                    logger.log(f"🎵 Aplicando Música Global Continua: {gm_obj.name} (File: {gm_obj.file.name})")
                    bg_audio = AudioFileClip(gm_obj.file.path)
                    clips_to_close.append(bg_audio)
                elif global_music_name and os.path.exists(global_music_name):
                    # v9.2: Fallback to direct absolute/relative path if DB lookup fails
                    logger.log(f"🎵 Aplicando Música Global Directa: {os.path.basename(global_music_name)}")
                    bg_audio = AudioFileClip(global_music_name)
                    clips_to_close.append(bg_audio)
                elif global_music_name:
                    # Try media-relative path as last resort
                    potential_path = os.path.join(settings.MEDIA_ROOT, global_music_name)
                    if os.path.exists(potential_path):
                        logger.log(f"🎵 Aplicando Música Global (Media): {os.path.basename(global_music_name)}")
                        bg_audio = AudioFileClip(potential_path)
                        clips_to_close.append(bg_audio)
                else:
                    logger.log(f"⚠️ No se pudo encontrar el archivo de música: {global_music_name}")
                    bg_audio = None
                
                if bg_audio:
                    # 2. Loop to full duration
                    loops = int(final_video.duration / bg_audio.duration) + 1
                    bg_audio_looped = bg_audio.with_effects([afx.AudioLoop(n_loops=loops)]).with_duration(final_video.duration)
                    
                    # 3. Global Volume Defaults
                    try:
                        default_vol = float(script.music_volume) if script.music_volume is not None else float(project.music_volume)
                    except (TypeError, ValueError):
                        default_vol = 0.20
                    
                    if default_vol <= 0: default_vol = 0.20
                    
                    # 4. Build Global Intervals & Volume Map
                    global_voice_intervals = []
                    mute_intervals = []
                    block_time_ranges = []
                    
                    current_offset = 0.0
                    for b_meta in block_metadata:
                        b_dur = b_meta['duration']
                        b_end = current_offset + b_dur
                        b_vol = b_meta.get('volume', default_vol)
                        block_time_ranges.append((current_offset, b_end, b_vol))
                        for v_start, v_end in b_meta['voice_intervals']:
                            global_voice_intervals.append((v_start + current_offset, v_end + current_offset))
                        if b_meta['has_local_music']:
                            mute_intervals.append((current_offset, b_end))
                        current_offset += b_dur

                    # 5. Dynamic Ducking (v5.8)
                    peak_vol = default_vol
                    duck_ratio = float(settings.AUDIO_DUCKING_RATIO)
                    attack_t = 0.2; release_t = 0.8

                    logger.log(f"    [Audio] Mezclando música global dinámica ({len(global_voice_intervals)} intervalos de voz)")

                    def volume_ducking_global(t):
                        if isinstance(t, np.ndarray):
                            base_vols = np.full(t.shape, peak_vol)
                            for b_start, b_end, b_vol in block_time_ranges:
                                mask = (t >= b_start) & (t <= b_end)
                                base_vols[mask] = b_vol
                            
                            factors = np.full(t.shape, 1.0)
                            for v_start, v_end in global_voice_intervals:
                                factors[(t >= v_start) & (t <= v_end)] = duck_ratio
                                m_out = (t >= (v_start - attack_t)) & (t < v_start)
                                if np.any(m_out):
                                    p = (t[m_out] - (v_start - attack_t)) / attack_t
                                    factors[m_out] = np.minimum(factors[m_out], 1.0 - (p * (1.0 - duck_ratio)))
                                m_in = (t > v_end) & (t <= (v_end + release_t))
                                if np.any(m_in):
                                    p = (t[m_in] - v_end) / release_t
                                    factors[m_in] = np.minimum(factors[m_in], duck_ratio + (p * (1.0 - duck_ratio)))
                            
                            for ms, me in mute_intervals:
                                factors[(t >= ms) & (t <= me)] = 0.0
                            
                            # v9.4 Fix: Ensure (N, 1) for stereo broadcasting
                            return (base_vols * factors)[:, None]
                        else:
                            try:
                                cur_peak = float(peak_vol)
                                for b_start, b_end, b_vol in block_time_ranges:
                                    if b_start <= t <= b_end:
                                        cur_peak = float(b_vol); break
                            except: cur_peak = 0.2
                            
                            for ms, me in mute_intervals:
                                if ms <= t <= me: return 0.0
                            
                            factor = 1.0
                            for v_start, v_end in global_voice_intervals:
                                if v_start <= t <= v_end: factor = min(factor, duck_ratio)
                                elif (v_start - attack_t) <= t < v_start:
                                    p = (t - (v_start - attack_t)) / attack_t
                                    factor = min(factor, 1.0 - (p * (1.0 - duck_ratio)))
                                elif v_end < t <= (v_end + release_t):
                                    p = (t - v_end) / release_t
                                    factor = min(factor, duck_ratio + (p * (1.0 - duck_ratio)))
                            return float(cur_peak * factor)

                    bg_audio_final = bg_audio_looped.transform(lambda get_f, t: get_f(t) * volume_ducking_global(t))
                    final_video = final_video.with_audio(CompositeAudioClip([final_video.audio, bg_audio_final]))
                    
        except Exception as e:
            logger.log(f"[Error] Error procesando música global: {e}")

        # 5. Render Final Video
        # ═══════════════════════════════════════════════════════════════════
        if final_video:
            project.progress = 90
            project.save(update_fields=['progress'])
            width, height = target_size # Ensure width/height are defined for logging
            logger.log(f"🎬 Iniciando renderizado final ({width}x{height})...")
            
            output_filename = f"video_{project.id}_{int(time.time())}.mp4"
            output_path = os.path.join(settings.MEDIA_ROOT, 'videos', output_filename)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # v5.9 GPU Preset Fix
            use_gpu = (project.render_mode == 'gpu')
            
            # v11.8: Stable rendering (Single Thread)
            render_params = {
                'fps': 30, 
                'codec': 'libx264', 
                'audio_codec': 'aac', 
                'preset': 'ultrafast', 
                'threads': 1
            }
            
            if use_gpu:
                logger.log("[HW] MODO RENDER: GPU Acelerado (NVENC)")
                render_params.update({
                    'codec': 'h264_nvenc', 
                    'bitrate': '5000k',
                    'preset': 'p1',  # Correct preset for NVENC (p1=fastest, p7=slowest/best)
                    'threads': None  # NVENC handles its own threads better
                })
            else:
                logger.log("[HW] MODO RENDER: CPU Standard (libx264)")

            # v11.1: Progress callback and optimized DB saving
            def set_progress(percent):
                new_val = round(float(percent), 1)
                # v11.2: I/O Optimization - Only save to DB if progress changed by at least 1%
                # to avoid hammering SQLite during final render which has many updates.
                old_val = getattr(set_progress, 'last_db_val', -1.0)
                if abs(new_val - old_val) >= 1.0 or new_val >= 99.0 or new_val <= 1.0:
                    project.progress_total = new_val
                    project.save(update_fields=['progress_total'])
                    set_progress.last_db_val = new_val
                else:
                    # Update in-memory only for logic
                    project.progress_total = new_val

            # v11.7: SILENT MODE (Maximum Stability)
            # Using None solves the 0.05s truncation bug and 0:00 duration error on Windows.
            # Progression will jump from 90% to 100% upon completion.
            set_progress(92) 

            final_video.write_videofile(
                output_path, 
                ffmpeg_params=["-pix_fmt", "yuv420p"], 
                logger=None, # v11.7: Stability over telemetry. Avoids truncated 0.05s videos.
                **render_params
            )
            
            project.output_video.name = f"videos/{output_filename}"
            project.duration = float(final_video.duration)
            project.timestamps = "\n".join(timestamps_list)
            project.status = 'completed'
            project.progress = 100
            project.save()
            
            logger.log(f"✅ ¡Video generado con éxito! ({output_path})")
        project.progress_total = 100.0 # Ensure final progress is 100%
        project.status = 'completed'; project.save()
        play_finish_sound(success=True)
        logger.log(f"[Done] Exito en {time.time()-start_time:.1f} segundos!")

    except Exception as e:
        logger.log(f"[FATAL] Error en renderizado: {e}")
        project.status = 'failed'; project.save()
        play_finish_sound(success=False)
        raise e
    finally:
        try:
            if 'final_video' in locals() and final_video: final_video.close()
            # v9.6: Explicit closure of all tracked clips before deletion
            for c in clips_to_close:
                try: c.close()
                except: pass
            
            for c in block_clips: 
                try: c.close()
                except: pass
                
            for _, p in audio_files: 
                if p and os.path.exists(p): 
                    try: os.remove(p)
                    except Exception as e:
                        logger.log(f"[Cleanup] No se pudo borrar {os.path.basename(p)}: {e}")
        except Exception as e:
            logger.log(f"[Cleanup] Error fatal en limpieza: {e}")
        
    return output_path
