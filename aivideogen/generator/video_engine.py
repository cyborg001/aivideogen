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

def apply_ken_burns(image_path, duration, target_size, zoom="1.0:1.3", move="HOR:50:50", overlay_path=None, fit=None):
    """
    Applies optimized Ken Burns effect with robust sizing and movement.
    Supports diagonal movement: "HOR:start:end + VER:start:end"
    """
    from moviepy import ImageClip, VideoFileClip, CompositeVideoClip, vfx
    from PIL import Image
    
    # ═══════════════════════════════════════════════════════════════════
    # 1. PARSE PARAMETERS
    # ═══════════════════════════════════════════════════════════════════
    # Expected format: "X:Y" (e.g. "1.0:1.3")
    z_parts = zoom.split(':') if (zoom and ':' in zoom) else ['1.0', '1.0']
    z_start = float(z_parts[0]) if len(z_parts) > 0 else 1.0
    z_end = float(z_parts[1]) if len(z_parts) > 1 else z_start
    
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
    img = Image.open(image_path)
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
        progress = t / duration
        rel_zoom = z_start + (z_end - z_start) * progress
        return rel_zoom / max(z_start, z_end)

    def get_frame_pos(t):
        progress = t / duration
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
        return (int(x), int(y))

    base_clip = ImageClip(img_np, duration=duration)
    clip = base_clip.resized(get_frame_scale).with_position(get_frame_pos)
    
    layers = [clip]
    if overlay_path and os.path.exists(overlay_path):
        overlay = VideoFileClip(overlay_path, has_mask=True)
        if overlay.duration < duration:
            overlay = overlay.with_effects([vfx.Loop(duration=duration)])
        overlay = overlay.resized(target_size).subclipped(0, duration)
        overlay = overlay.with_mask(overlay.to_mask()).with_opacity(0.4).without_audio()
        layers.append(overlay)
    
    return CompositeVideoClip(layers, size=target_size, bg_color=(0,0,0)).with_duration(duration)


def process_video_asset(video_path, duration, target_size, overlay_path=None, fit=None):
    """
    Processes a video asset to fit the scene: looping, trimming, and scaling.
    """
    from moviepy import VideoFileClip, CompositeVideoClip, vfx
    
    # Load video
    v_clip = VideoFileClip(video_path)
    
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
    
    # Log Video Format
    format_type = "SHORT" if project.aspect_ratio == 'portrait' else "VIDEO"
    logger.log(f"📐 FORMATO: {format_type}")
    
    # Parse script
    try:
        script = parse_avgl_json(project.script_text)
        logger.log(f"✅ Script parseado: '{script.title}'")
    except Exception as e:
        logger.log(f"❌ Error al parsear JSON: {e}")
        project.status = 'error'
        project.save()
        return
    
    # Update project title if specified and NOT already set by user manually
    if script.title and project.title in ["Sin Título", "Video Sin Título", "Proyecto sin título", ""]:
        project.title = script.title
        project.save()

    # FORCE OVERRIDE: Apply Project Voice to Script
    # This ensures "Dominican" request overrides "Alvaro" default in parse_avgl_json
    if project.voice_id:
        logger.log(f"🎤 Forzando voz del proyecto: {project.voice_id}")
        script.voice = project.voice_id
        # Propagate to all existing scenes that have default/None
        for block in script.blocks:
            for scene in block.scenes:
                # If scene specific voice is same as default or empty, override
                if not scene.voice or scene.voice == "es-ES-AlvaroNeural":
                    scene.voice = project.voice_id
    
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
    
    # Generate Audio for all scenes
    audio_files = []
    from moviepy import AudioClip
    
    for i, scene in enumerate(all_scenes):
        logger.log(f"  Escena {i+1}/{len(all_scenes)}: {scene.title}")
        
        audio_path = os.path.join(temp_audio_dir, f"project_{project.id}_scene_{i:03d}.mp3")
        
        # If no text, create a tiny silent file or handle as None
        if not scene.text:
            # We skip generation but we will handle it in the next loop with a placeholder
            audio_files.append({
                "scene": scene,
                "path": None,
                "intervals": []
            })
            continue
            
        # Prepare text - Use clean mode (no SSML) for Edge TTS for now
        use_ssml = (project.engine == 'eleven')
        
        # CLEANUP: Strip Character Tags [NAME] from start of text
        # This prevents TTS from reading "[ETHAN]" and fixes potential "No audio" errors
        # CLEANUP: Strip Character Tags [NAME] from start of text
        # REMOVED: Legacy logic was stripping emotion tags like [TENSO].
        # The script is already cleaned of [NAME] tags.
        curr_text = scene.text

        # CLEANUP: Strip Stage Directions (Parentheses)
        # Prevents reading "(Susurrando)" aloud.
        curr_text = re.sub(r'\(.*?\)', '', curr_text)
        
        # CLEANUP: Strip Subtitle Tags [SUB:...] 
        # These are handled by the video renderer, but must be hidden from TTS
        curr_text = re.sub(r'\[SUB:.*?\]', '', curr_text).strip()

        text_with_emotions = translate_emotions(curr_text, use_ssml=use_ssml)
        
        if project.engine == 'edge':
            # SPEED LOGIC:
            # 1. If scene.speed != 1.0, use it.
            # 2. Else, check EDGE_TTS_RATE env var default.
            
            env_rate = os.getenv("EDGE_TTS_RATE", "+0%")
            
            if scene.speed != 1.0:
                speed_rate = f"{int((scene.speed - 1.0) * 100):+}%"
            else:
                speed_rate = env_rate

            # DEBUG: Log exact params being sent
            clean_debug = text_with_emotions.replace('<', '{').replace('>', '}')
            logger.log(f"    🎤 DEBUG EdgeTTS: Voice='{scene.voice}' Rate='{speed_rate}' Pitch='{scene.pitch}' Text='{clean_debug[:50]}...'")

            # CRITICAL FIX: Do NOT wrap in SSML here. generate_audio_edge handles segmentation manually.
            # Wrapping it in SSML breaks the regex for [TAGS] inside.
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success, intervals = loop.run_until_complete(
                generate_audio_edge(text_with_emotions, audio_path, scene.voice, rate=speed_rate, pitch=scene.pitch or "+0Hz")
            )
            loop.close()
        else:
            api_key = os.getenv('ELEVENLABS_API_KEY')
            voice_id = os.getenv('ELEVENLABS_VOICE_ID', 'EXAVITQu4vr4xnSDxMaL')
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            # ElevenLabs doesn't support segmented intervals yet, so we treat it as 1 single block
            success = loop.run_until_complete(
                generate_audio_elevenlabs(text_with_emotions, audio_path, voice_id, api_key)
            )
            loop.close()
            intervals = [] # Will be handled by fallback if empty
        
        if success:
            # We store the intervals along with the path
            audio_files.append({
                "scene": scene,
                "path": audio_path,
                "intervals": intervals
            })
        else:
            logger.log(f"  ⚠️ Error generando audio para escena {i+1}")
            audio_files.append({
                "scene": scene,
                "path": None,
                "intervals": []
            })
    
    # Check if we have at least some audio or scenes
    if not audio_files:
        logger.log("❌ No se detectaron escenas para procesar.")
        project.status = 'error'; project.save()
        return

    # CHECK CANCELLATION AFTER AUDIO
    project.refresh_from_db()
    if project.status == 'cancelled':
        logger.log("🛑 Generación detenida por usuario (post-audio).")
        return

    # ═══════════════════════════════════════════════════════════════════
    # GROUP MASTER SHOT INTERPOLATION (Constant Velocity)
    # ═══════════════════════════════════════════════════════════════════
    # Group scenes by group_id to recalculate Zoom/Move based on ACTUAL audio duration.
    # This overrides the initial text-length based estimation for perfect constant speed.
    group_tracker = {}
    
    # 1. Collect Durations
    for item in audio_files:
        scn = item['scene']
        path = item['path']
        if not scn.group_id: continue
        
        # Get duration
        dur = 0.5 # default safety
        if path and os.path.exists(path):
            try:
                # We use a quick probe or AudioFileClip (heavy)
                # Since we already use MoviePy later, let's just peek or trust metadata if we had it.
                # But we don't have metadata yet. MoviePy is safe here as we need it anyway.
                # Optimization: Cache duration in item to avoid double load?
                temp_clip = AudioFileClip(path)
                dur = temp_clip.duration
                temp_clip.close()
                item['duration'] = dur # Cache for later loop
            except: pass
        else:
            dur = 1.0 # fallback for silence
            item['duration'] = dur
            
        dur += scn.pause # Add pause to visual duration
        
        if scn.group_id not in group_tracker:
            group_tracker[scn.group_id] = {
                "scenes": [],
                "settings": scn.group_settings,
                "total_duration": 0.0
            }
        
        group_tracker[scn.group_id]["scenes"].append(item)
        group_tracker[scn.group_id]["total_duration"] += dur

    # 2. Re-Interpolate
    for gid, gdata in group_tracker.items():
        total_dur = gdata["total_duration"] or 1.0
        current_time = 0.0
        
        # Parse Group Settings
        # Zoom
        z_start, z_end = 1.0, 1.1
        if gdata["settings"] and gdata["settings"].get("zoom"):
            z_parts = gdata["settings"]["zoom"].split(':')
            if len(z_parts) >= 2: 
                try: z_start = float(z_parts[0]); z_end = float(z_parts[1])
                except: pass
        
        # Move
        move_str = gdata["settings"].get("move") or ""
        # We need to support the multi-move string parsing logic here again? 
        # Or just construct the interpolation ratios and let apply_ken_burns handle the parsing of start/end.
        # Issue: apply_ken_burns takes "zoom=1.0:1.2" string. We need to construct that string per scene.
        # Ideally we parse move dimensions (HOR, VER) separately.
        
        moves_parsed = []
        if move_str:
            parts = move_str.split('+')
            for p in parts:
                mp = p.strip().split(':')
                if len(mp) >= 3:
                    moves_parsed.append({
                        "dim": mp[0].strip(),
                        "start": float(mp[1]),
                        "end": float(mp[2])
                    })

        for item in gdata["scenes"]:
            scene_dur = item.get("duration", 0)
            
            # Start/End Ratios
            r_start = current_time / total_dur
            r_end = (current_time + scene_dur) / total_dur
            
            # Interpolate Zoom
            s_z_start = z_start + (z_end - z_start) * r_start
            s_z_end = z_start + (z_end - z_start) * r_end
            new_zoom_str = f"{s_z_start:.3f}:{s_z_end:.3f}"
            
            # Interpolate Move
            new_move_parts = []
            for m in moves_parsed:
                s_m_start = m["start"] + (m["end"] - m["start"]) * r_start
                s_m_end = m["start"] + (m["end"] - m["start"]) * r_end
                new_move_parts.append(f"{m['dim']}:{s_m_start:.1f}:{s_m_end:.1f}")
            
            new_move_str = " + ".join(new_move_parts) if new_move_parts else ""
            
            # Update Scene Asset
            if item['scene'].assets:
                asset = item['scene'].assets[0]
                asset.zoom = new_zoom_str
                if new_move_str: asset.move = new_move_str
            
            current_time += scene_dur

    # ═══════════════════════════════════════════════════════════════════
    # SCENE-BY-SCENE GENERATION (Robust Sync)
    # ═══════════════════════════════════════════════════════════════════
    from moviepy import afx, AudioClip, AudioFileClip, CompositeAudioClip, TextClip, concatenate_videoclips, ImageClip
    block_clips = []
    block_metadata = []
    current_time = 0
    timestamps_list = []
    
    # Create a Scene-to-Audio mapping to prevent desync
    # Now it maps scene to a dict with 'path' and 'intervals'
    scene_audio_map = {item['scene']: item for item in audio_files}
    
    for b_idx, block in enumerate(script.blocks):
        # CHECK CANCELLATION
        project.refresh_from_db()
        if project.status == 'cancelled':
            logger.log("🛑 Generación detenida por usuario (dentro del bucle de bloques).")
            return

        logger.log(f"📦 Procesando Bloque {b_idx+1}: {block.title}")
        block_scene_clips = []
        block_voice_intervals = []
        block_cursor = 0.0
        
        # Continuity Tracking (Per Block)
        last_asset_path = None
        last_zoom_end = 1.0
        last_move = None
        
        for s_idx, scene in enumerate(block.scenes):
            # 0. GRANULAR CANCELLATION CHECK (v2.25.1)
            project.refresh_from_db()
            if project.status == 'cancelled':
                logger.log("🛑 Generación detenida por usuario (en bucle de escenas).")
                return

            # 1. Audio Retrieval (Robust)
            audio_clip = None
            scene_intervals = []
            if scene in scene_audio_map:
                audio_entry = scene_audio_map[scene]
                if audio_entry['path']:
                    audio_clip = AudioFileClip(audio_entry['path'])
                    scene_intervals = audio_entry.get('intervals', [])
            
            # Fallback for missing audio (ensures sync)
            if not audio_clip:
                logger.log(f"  ⚠️ Audio NO generado per escena {s_idx+1}. Usando silencio.")
                audio_clip = AudioClip(lambda t: [0,0], duration=1.0)
                # If no intervals, we treat as a single block if it's fallback
                scene_intervals = [(0, audio_clip.duration)]
            
            # If engine didn't provide intervals (e.g. ElevenLabs or single block fallback)
            if not scene_intervals:
                scene_intervals = [(0, audio_clip.duration)]

            duration = audio_clip.duration + scene.pause
            
            # REVERT: Use only the first asset
            if scene.assets:
                asset = scene.assets[0]
                
                # CRITICAL FIX v2.26.1: Check if asset.type is valid before join
                if not asset.type:
                     logger.log(f"  ⚠️ Asset sin tipo definido en escena {s_idx+1}. Ignorando.")
                     asset_path = "__INVALID__"
                else:
                     # Check if it's already an absolute path or exists relative to CWD
                     if os.path.exists(asset.type) or os.path.isabs(asset.type):
                         asset_path = asset.type
                     else:
                         asset_path = os.path.join(assets_dir, asset.type)
                
                # Tolerance for common extensions
                if not os.path.exists(asset_path):
                    for ext in ['.png', '.jpg', '.jpeg', '.mp4']:
                        if os.path.exists(asset_path + ext):
                            asset_path += ext; break

                if not os.path.exists(asset_path):
                    logger.log(f"  ⚠️ Asset no encontrado o inválido: {asset.type}. Fondo negro.")
                    clip = ImageClip(np.zeros((target_size[1], target_size[0], 3), dtype=np.uint8), duration=duration)
                    
                    # Reset continuity on missing asset
                    last_asset_path = None
                    last_zoom_end = 1.0
                    last_move = None
                    
                else:
                    eff_zoom = asset.zoom or "1.0:1.3"
                    eff_move = asset.move or "HOR:50:50"

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
                            fit=asset.fit
                        )
                    else:
                        # Apply Ken Burns (Standard image logic)
                        clip = apply_ken_burns(
                            asset_path, duration, target_size,
                            zoom=eff_zoom,
                            move=eff_move,
                            overlay_path=overlay_path, 
                            fit=asset.fit
                        )
            else:
                clip = ImageClip(np.zeros((target_size[1], target_size[0], 3), dtype=np.uint8), duration=duration)
            
            # 2. SFX Processing (New)
            scene_sfx_clips = []
            if scene.sfx:
                sfx_dir = os.path.join(settings.MEDIA_ROOT, 'sfx')
                for sfx_item in scene.sfx:
                    sfx_path = os.path.join(sfx_dir, sfx_item.type)
                    # Tolerance for extension
                    if not os.path.exists(sfx_path):
                        for ext in ['.mp3', '.wav']:
                            if os.path.exists(sfx_path + ext):
                                sfx_path += ext; break
                    
                    if os.path.exists(sfx_path):
                        try:
                            s_clip = AudioFileClip(sfx_path).with_effects([afx.MultiplyVolume(sfx_item.volume)])
                            
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

            # SUBTITLE RENDERING v3.2 (Calculated Offsets)
            scene_subtitles = []
            if hasattr(scene, 'subtitles') and scene.subtitles:
                scene_subtitles = scene.subtitles
            elif hasattr(scene, 'subtitle') and scene.subtitle:
                # Compatibility with old single subtitle format
                scene_subtitles = [{"text": scene.subtitle, "offset": 0, "duration": duration}]

            if scene_subtitles:
                try:
                    from moviepy import CompositeVideoClip
                    
                    # Font selection
                    font = 'Arial'
                    font_candidates = [
                        r'C:\Windows\Fonts\arial.ttf',
                        r'C:\Windows\Fonts\Arial.ttf',
                        r'C:\Windows\Fonts\segoeui.ttf',
                        r'C:\Windows\Fonts\verdana.ttf'
                    ]
                    for candidate in font_candidates:
                        if os.path.exists(candidate):
                            font = candidate; break
                    
                    # Calculate Word Duration for Sync
                    # Logic: (audio_duration / word_count)
                    clean_text = re.sub(r'\[.*?\]', '', scene.text)
                    words = clean_text.split()
                    word_count = len(words)
                    
                    # Prevent division by zero, use a safe default if no words
                    word_duration = (audio_clip.duration / word_count) if word_count > 0 else 0.5
                    
                    subtitle_clips = []
                    fontsize = int(target_size[1] * 0.06) 
                    
                    for sub in scene_subtitles:
                        sub_text = sub.get('text', '')
                        if not sub_text: continue
                        
                        # Calculate Timing v4.0 (Word Count Based)
                        # START TIME: word_index * word_duration
                        sub_start = sub.get('offset', 0) * word_duration
                        
                        # DURATION: word_count * word_duration
                        sub_word_count = sub.get('word_count')
                        if sub_word_count:
                            sub_dur = int(sub_word_count) * word_duration
                        else:
                            sub_dur = 3 # Fallback (v4.5 standard)
                            
                        # Ensure it fits in scene (Grace period of 0.1s)
                        final_dur = min(sub_dur, (duration + 0.1) - sub_start)
                        if final_dur < 0.1: continue 
                        
                        # Ensure start is within scene
                        if sub_start >= duration: continue
                        
                        # STYLE v4.3 PRO (Compatibility Fix)
                        from moviepy import ColorClip
                        
                        try:
                            txt_content = sub_text.upper()
                            
                            # BOX DIMENSIONS: Force Integer!
                            temp_size_txt = TextClip(text=txt_content, font_size=fontsize, font=font, color='yellow', method='label')
                            box_w = int(temp_size_txt.w + 120)
                            box_h = int(temp_size_txt.h + 60)
                            temp_size_txt.close()
                            
                            # 1. Create Text Clip using 'caption'
                            # 'align' is removed due to compatibility error in this environment
                            txt_clip = TextClip(
                                text=txt_content,
                                font_size=fontsize,
                                color='yellow',
                                font=font,
                                stroke_color='black',
                                stroke_width=2,
                                method='caption',
                                size=(box_w, box_h)
                            )
                            
                            # 2. Black Background: Force Integer!
                            bg_clip = ColorClip(size=(int(box_w), int(box_h)), color=(0,0,0)).with_opacity(1.0)
                            
                            # 3. Composite (Stacking)
                            sub_box = CompositeVideoClip([bg_clip, txt_clip], size=(int(box_w), int(box_h)))
                            
                            # 4. Final Timing & Positioning
                            final_sub = sub_box.with_position(('center', 0.80), relative=True)\
                                               .with_start(sub_start)\
                                               .with_duration(final_dur)\
                                               .with_end(sub_start + final_dur)
                            
                            subtitle_clips.append(final_sub)
                            logger.log(f"    📝 Subtítulo v4.3: '{sub_text}' ({sub_start:.2f}s, words:{sub_word_count})")
                        except Exception as sub_err:
                            logger.log(f"    ⚠️ Error v4.3 Rendering: {sub_err}")
                            # Fallback
                            txt_clip = TextClip(text=sub_text, font_size=fontsize, color='yellow', bg_color='black', method='caption', size=(int(target_size[0]*0.8), None))
                            subtitle_clips.append(txt_clip.with_position(('center', 0.80), relative=True).with_start(sub_start).with_duration(final_dur).with_end(sub_start + final_dur))

                    if subtitle_clips:
                        clip = CompositeVideoClip([clip] + subtitle_clips)
                    
                except Exception as e:
                    logger.log(f"    ⚠️ Error renderizando subtítulos: {e}")

            # Set audio & append
            clip = clip.with_audio(audio_clip)
            block_scene_clips.append(clip)
            
            # Timestamps
            mins, secs = divmod(int(current_time), 60)
            timestamps_list.append(f"{mins:02d}:{secs:02d} - {scene.title}")
            
            # Track voice interval for ducking (relative to block start)
            # SMART DUCKING: Shift all sub-intervals by the block_cursor
            for v_start, v_end in scene_intervals:
                block_voice_intervals.append((block_cursor + v_start, block_cursor + v_end))
            
            current_time += duration
            block_cursor += duration
        
        if not block_scene_clips: continue
        
        # Concatenate block scenes
        block_video = concatenate_videoclips(block_scene_clips, method="compose")
        
        # Track intervals globally for post-loop music processing
        for start, end in block_voice_intervals:
            # Shift interval by current block start time (calculated by tracking cumulative duration)
            # wait, 'block_cursor' was relative to 0 at start of loop.
            # We need the absolute time.
            # Let's calculate absolute start of this block
            # Actually, we can just use the fact that we concatenate later.
            # We need to store (block_duration, voice_intervals_relative, has_local_music)
            pass

        # Apply Block Music ONLY if explicitly set in block
        music_to_use = block.music
        has_local_music = False
        
        if music_to_use:
            try:
                from .models import Music
                m_obj = Music.objects.filter(file__icontains=music_to_use).first() or \
                        Music.objects.filter(name__icontains=music_to_use).first()
                
                if m_obj and os.path.exists(m_obj.file.path):
                    has_local_music = True
                    logger.log(f"  🎵 Música específica bloque: {m_obj.name}")
                    bg_audio = AudioFileClip(m_obj.file.path)
                    
                    loops = int(block_video.duration / bg_audio.duration) + 1
                    bg_audio_looped = bg_audio.with_effects([afx.AudioLoop(n_loops=loops)]).with_duration(block_video.duration)
                    
                    vol = block.volume if block.volume is not None else 0.2
                    
                    # Local Ducking
                    peak_vol = vol
                    duck_vol = peak_vol * 0.12
                    attack_t = 0.3; release_t = 1.5

                    def volume_ducking_local(t):
                         # ... (Same logic as before but strictly local) ...
                        if isinstance(t, np.ndarray):
                            vol_arr = np.full(t.shape, peak_vol)
                            for start, end in block_voice_intervals:
                                vol_arr[(t >= start) & (t <= end)] = duck_vol
                                mask_fade_out = (t >= (start - attack_t)) & (t < start)
                                if np.any(mask_fade_out):
                                    progress = (t[mask_fade_out] - (start - attack_t)) / attack_t
                                    vol_arr[mask_fade_out] = peak_vol - (progress * (peak_vol - duck_vol))
                                mask_fade_in = (t > end) & (t <= (end + release_t))
                                if np.any(mask_fade_in):
                                    progress = (t[mask_fade_in] - end) / release_t
                                    vol_arr[mask_fade_in] = duck_vol + (progress * (peak_vol - duck_vol))
                            return vol_arr.reshape(-1, 1)
                        else:
                             for start, end in block_voice_intervals:
                                if start <= t <= end: return duck_vol
                                if (start - attack_t) <= t < start:
                                    progress = (t - (start - attack_t)) / attack_t
                                    return peak_vol - (progress * (peak_vol - duck_vol))
                                if end < t <= (end + release_t):
                                    progress = (t - end) / release_t
                                    return duck_vol + (progress * (peak_vol - duck_vol))
                             return peak_vol

                    bg_audio_final = bg_audio_looped.transform(lambda get_f, t: get_f(t) * volume_ducking_local(t))
                    final_audio = CompositeAudioClip([block_video.audio, bg_audio_final])
                    block_video = block_video.with_audio(final_audio)
            except Exception as e:
                logger.log(f"  ⚠️ Error música bloque: {e}")

        # Store metadata for Global Music Pass
        bs_vol = block.volume if block.volume is not None else (script.music_volume if script.music_volume is not None else 0.18)
        block_metadata.append({
            'duration': block_video.duration,
            'voice_intervals': block_voice_intervals, # Current Relative
            'has_local_music': has_local_music,
            'volume': bs_vol
        })
        
        block_clips.append(block_video)

    if not block_clips:
        logger.log("❌ Error fatal: No se generaron clips de bloques.")
        project.status = 'failed'; project.save()
        return

    logger.log("🔗 Concatenando bloques y exportando...")
    final_video = concatenate_videoclips(block_clips, method="compose")
    
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
            from .models import Music
            gm_obj = Music.objects.filter(file__icontains=global_music_name).first() or \
                     Music.objects.filter(name__icontains=global_music_name).first()
            
            if gm_obj and os.path.exists(gm_obj.file.path):
                logger.log(f"🎵 Aplicando Música Global Continua: {gm_obj.name}")
                bg_audio = AudioFileClip(gm_obj.file.path)
                
                # Loop to full duration
                loops = int(final_video.duration / bg_audio.duration) + 1
                bg_audio_looped = bg_audio.with_effects([afx.AudioLoop(n_loops=loops)]).with_duration(final_video.duration)
                
                # Global Volume Defaults
                default_vol = script.music_volume if script.music_volume is not None else project.music_volume
                if default_vol is None: default_vol = 0.20
                
                # 2. Build Global Intervals & Volume Map
                global_voice_intervals = []
                mute_intervals = []
                # block_time_ranges = list of (start, end, volume)
                block_time_ranges = []
                
                current_offset = 0.0
                
                for b_meta in block_metadata:
                    b_dur = b_meta['duration']
                    b_end = current_offset + b_dur
                    
                    # Store block volume range
                    # Fallback to default if block volume is None (though we handled it above)
                    b_vol = b_meta.get('volume', default_vol)
                    block_time_ranges.append((current_offset, b_end, b_vol))
                    
                    # Offset local voice intervals to global time
                    for v_start, v_end in b_meta['voice_intervals']:
                        global_voice_intervals.append((v_start + current_offset, v_end + current_offset))
                    
                    # If block has local music, we must MUTE global music here
                    if b_meta['has_local_music']:
                        mute_intervals.append((current_offset, b_end))
                        
                    current_offset += b_dur

                # 3. Global Ducking & Muting & Volume Automation Function
                # Legacy "Snappy" Ducking (Precision Calibration v2.26 - Aggressive)
                duck_factor = 0.25  # Duck to 25% of peak (0.20 * 0.25 = 0.05 Target - "Almost Null")
                fade_t = 0.25       # Attack Time (Fast but smooth)
                release_t = 1.6     # Release Time (Slow - Prevents pumping in short pauses)
                fade_muting = 0.5 

                def volume_global(t):
                    # Helper for scalar/vector t
                    args = t if isinstance(t, np.ndarray) else np.array([t])
                    
                    # 1. Base Volume (From JSON or Block Override)
                    # For simplicity and "Snappy" feel, we stick to Global Peak mostly, 
                    # but allow Block Logic to override the CEILING.
                    vol_arr = np.full(args.shape, default_vol)
                    
                    # Apply Block Specific Volumes (e.g. Conclusion = 0.05)
                    for start, end, b_vol in block_time_ranges:
                        mask_block = (args >= start) & (args < end)
                        if np.any(mask_block):
                            vol_arr[mask_block] = b_vol

                    # 2. Ducking (Voices) - Linear Transformation relative to Base
                    for start, end in global_voice_intervals:
                        # Find Base Volume at this moment (Dynamic Baseline)
                        # We use a simplified approach: calculate ducked target from the CURRENT base
                        
                        # Full Duck Region
                        mask_voice = (args >= start) & (args <= end)
                        if np.any(mask_voice):
                            vol_arr[mask_voice] *= duck_factor
                        
                        # Attack (Fade Out: Base -> Duck)
                        mask_out = (args >= (start - fade_t)) & (args < start)
                        if np.any(mask_out):
                            # Linear progression 0.0 -> 1.0
                            prog = (args[mask_out] - (start - fade_t)) / fade_t
                            curr_base = vol_arr[mask_out] # This is currently High
                            target_duck = curr_base * duck_factor
                            vol_arr[mask_out] = curr_base - (prog * (curr_base - target_duck))

                        # Release (Fade In: Duck -> Base)
                        mask_in = (args > end) & (args <= (end + release_t))
                        if np.any(mask_in):
                            # Linear progression 0.0 -> 1.0
                            prog = (args[mask_in] - end) / release_t
                            # For Release, we want to go FROM Duck TO Base
                            # But vol_arr in this region is currently Base (untouched by mask_voice)
                            curr_base = vol_arr[mask_in]
                            base_duck = curr_base * duck_factor
                            vol_arr[mask_in] = base_duck + (prog * (curr_base - base_duck))

                    # 3. Muting (Local Music Blocks)
                    for start, end in mute_intervals:
                        vol_arr[(args >= start) & (args <= end)] = 0
                        # Fade out
                        mask_out = (args >= (start - fade_muting)) & (args < start)
                        if np.any(mask_out):
                            prog = (args[mask_out] - (start - fade_muting)) / fade_muting
                            vol_arr[mask_out] *= (1.0 - prog)
                        # Fade in
                        mask_in = (args > end) & (args <= (end + fade_muting))
                        if np.any(mask_in):
                            prog = (args[mask_in] - end) / fade_muting
                            vol_arr[mask_in] *= prog

                    return vol_arr.reshape(-1, 1) if isinstance(t, np.ndarray) else vol_arr[0]

                # Apply
                bg_audio_final = bg_audio_looped.transform(lambda get_f, t: get_f(t) * volume_global(t))
                
                # Check for cancellations before expensive mix
                project.refresh_from_db()
                if project.status == 'cancelled': return

                final_audio = CompositeAudioClip([final_video.audio, bg_audio_final])
                final_video = final_video.with_audio(final_audio)
                
    except Exception as e:
        logger.log(f"⚠️ Error procesando música global: {e}")

    output_filename = f"project_{project.id}.mp4"
    output_path = os.path.join(settings.MEDIA_ROOT, 'videos', output_filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # FINAL CANCELLATION CHECK BEFORE RENDER (v2.25.1)
    project.refresh_from_db()
    if project.status == 'cancelled':
        logger.log("🛑 Renderizado abortado por usuario.")
        try: final_video.close()
        except: pass
        return

    final_video.write_videofile(
        output_path, fps=30, codec='libx264', audio_codec='aac', 
        preset='ultrafast', threads=8
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
