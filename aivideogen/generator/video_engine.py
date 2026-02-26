"""
AVGL v4.0 - Video Generation Engine
Handles the complete video rendering pipeline with optimizations
"""

import os
import time
import re
import numpy as np
import logging
import proglog
from django.conf import settings
from .subtitle_utils import compile_full_script_ass

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


def safe_float(val, default=0.0):
    try:
        if val is None or str(val).strip() == "": return default
        return float(val)
    except:
        return default

# ═══════════════════════════════════════════════════════════════════
# MONKEY PATCH: Absolute Audio Immunity (v15.9)
# ═══════════════════════════════════════════════════════════════════
try:
    from moviepy.audio.io.readers import FFMPEG_AudioReader
    _original_get_frame = FFMPEG_AudioReader.get_frame

    def _patched_get_frame(self, tt):
        try:
            # v14.9 Trace: Log if silence is being injected
            if hasattr(tt, "__len__") and len(tt) > 0:
                pass # Normal operation log would be too noisy here
            
            # Fix 2: Execute original but catch ANY internal error (like out of bounds)
            return _original_get_frame(self, tt)
            
        except Exception as e:
            # If moviepy logic fails internally (math errors, corrupt buffer access)
            # return silent buffer instead of crashing the whole video
            try:
                # Calculate required shape
                length = len(tt) if hasattr(tt, "__len__") else 1
                return np.zeros((length, self.nchannels))
            except:
                return np.zeros((0, 2)) # Absolute fallback

    FFMPEG_AudioReader.get_frame = _patched_get_frame
    logger.info("🛡️ [SYSTEM] Absolute Audio Immunity Active (MoviePy patched).")
except Exception as e:
    logger.warning(f"⚠️ [SYSTEM] Could not apply Audio Immunity: {e}")

def fast_mux_audio_video(video_path, audio_path, output_path, video_volume=1.0):
    """
    v15.0: Direct FFmpeg Muxing (Stream Copy)
    Combines video and audio without re-encoding pixels.
    Nearly instantaneous.
    """
    import subprocess
    
    # v15.4: Clean Replacement (No amix)
    # The new audio_path TOTALLY replaces the video's original audio.
    # This prevents tone/speed alterations and keeps the process simple.
    cmd = [
        'ffmpeg', '-i', video_path, '-i', audio_path,
        '-c:v', 'copy', 
        '-c:a', 'aac', 
        '-map', '0:v:0', '-map', '1:a:0',
        '-shortest', '-y', output_path
    ]

    # Apply volume to the NEW audio if specified (rare in fast mode but supported)
    if video_volume != 1.0 and video_volume > 0:
        cmd = [
            'ffmpeg', '-i', video_path, '-i', audio_path,
            '-c:v', 'copy',
            '-filter_complex', f'[1:a]volume={video_volume}[a]',
            '-map', '0:v:0', '-map', '[a]',
            '-c:a', 'aac',
            '-shortest', '-y', output_path
        ]

    logger.info(f"🚀 [FastAssembly] Ejecutando Muxing de Reemplazo: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except Exception as e:
        logger.error(f"❌ [FastAssembly] Error en Muxing: {e}")
        if hasattr(e, 'stderr'): logger.error(f"   Stderr: {e.stderr}")
        return False
# ═══════════════════════════════════════════════════════════════════

def apply_ken_burns(image_path, duration, target_size, zoom="1.0:1.3", move="HOR:50:50", overlay_path=None, fit=None, shake=False, rotate=None, shake_intensity=5, w_rotate=None):
    """
    Applies optimized Ken Burns effect with robust sizing and movement.
    Supports diagonal movement: "HOR:start:end + VER:start:end"
    v11.8: Added SHAKE and ROTATE support.
    """
    import cv2
    import numpy as np
    from moviepy import VideoClip, CompositeVideoClip, VideoFileClip, vfx

    # ═══════════════════════════════════════════════════════════════════
    # 1. READ IMAGE & PARSE PARAMS
    # ═══════════════════════════════════════════════════════════════════
    if not image_path or not os.path.isfile(image_path):
        logger.error(f"❌ [apply_ken_burns] Ruta inválida: {image_path}")
        from moviepy import ColorClip
        return ColorClip(size=target_size, color=(0,0,0), duration=duration)

    # Load Full Resolution Image (OpenCV reads BGR)
    # Using cv2.imdecode to handle standard paths, or simple imread
    # We use Img decoding to ensure unicode path support if needed, but imread is usually fine
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        logger.error(f"❌ [apply_ken_burns] OpenCV no pudo leer: {image_path}")
        from moviepy import ColorClip
        return ColorClip(size=target_size, color=(0,0,0), duration=duration)

    h_orig, w_orig = img_bgr.shape[:2]
    target_w, target_h = target_size

    # Parse Zoom
    z_start, z_end = 1.0, 1.0
    if zoom:
        if isinstance(zoom, str) and ':' in zoom:
            parts = zoom.split(':')
            z_start = float(parts[0])
            z_end = float(parts[1])
        else:
            try:
                z_start = float(zoom)
                z_end = z_start
            except: pass

    # Parse Move
    # Supports "HOR:0:100 + VER:50:50" or simple "HOR:0:100"
    move_configs = []
    move_str = move if move else "HOR:50:50"
    
    # Check for Portrait Auto-Scan hack
    is_portrait = h_orig / w_orig > 1.2
    if is_portrait and not move:
        move_str = "VER:100:0"
    
    sub_moves = move_str.split('+')
    for sm in sub_moves:
        parts = sm.strip().split(':')
        mdir = parts[0].upper()
        mstart = float(parts[1]) if len(parts) > 1 else 50.0
        mend = float(parts[2]) if len(parts) > 2 else mstart
        move_configs.append({'dir': mdir, 'start': mstart, 'end': mend})

    # ═══════════════════════════════════════════════════════════════════
    # 2. CALCULATE CROP GEOMETRY
    # ═══════════════════════════════════════════════════════════════════
    # We need a base rectangle that fits/covers the target aspect ratio
    # Then we zoom into that rectangle.
    
    # Target Aspect Ratio
    tar_ar = target_w / target_h
    img_ar = w_orig / h_orig

    is_fit = (fit == "contain" or fit is True)

    # Base Crop Size (The "1.0" zoom level)
    # Usually we want to COVER the target.
    # If Image is wider than Target, height limits.
    # If Image is taller than Target, width limits.
    
    # Determine the maximum crop size that maintains target aspect ratio
    if is_fit:
        # FIT (Contain) Logic: The "window" is larger than the image in the dimension that doesn't fit.
        if img_ar > tar_ar:
            # Image is wider than target. Width is the limiting factor for containment.
            base_w = w_orig
            base_h = int(w_orig / tar_ar)
        else:
            # Image is taller/squarer than target. Height is the limiting factor for containment.
            base_h = h_orig
            base_w = int(h_orig * tar_ar)
    else:
        # COVER Logic (Default)
        if img_ar > tar_ar:
            # Image is wider (Landscape source, Portrait target?)
            # Max height, calculated width
            base_h = h_orig
            base_w = int(h_orig * tar_ar)
        else:
            # Image is taller/squarer
            # Max width, calculated height
            base_w = w_orig
            base_h = int(w_orig / tar_ar)

    # ═══════════════════════════════════════════════════════════════════
    # 3. FAST OPENCV MAKE_FRAME
    # ═══════════════════════════════════════════════════════════════════
    def make_frame(t):
        if duration == 0: progress = 0
        else: progress = t / duration

        # 1. Current Zoom Level
        # Note: In our previous logic, scale was inverse? 
        # Usually Ken Burns: Zoom 1.0 = Full Cover. Zoom 1.5 = Crop is smaller (1/1.5)
        # Let's align with logic: Zoom > 1 means "Zoom In" -> Show smaller area.
        current_zoom = z_start + (z_end - z_start) * progress
        scale_factor = 1.0 / current_zoom

        # Dimensions of the crop at this moment
        curr_w = base_w * scale_factor
        curr_h = base_h * scale_factor

        # 2. Current Pan Position (Center of the crop)
        # We navigate the "Slack" - the space between the crop and the image edges.
        # Slack dimensions
        slack_w = w_orig - curr_w
        slack_h = h_orig - curr_h

        # Default Center
        center_x = w_orig / 2
        center_y = h_orig / 2
        
        # Apply offsets based on Moves
        # 0% = Left/Top, 100% = Right/Bottom
        # Center = 50%
        
        # Accumulate normalized offsets (-0.5 to 0.5)
        off_x = 0.0
        off_y = 0.0
        
        has_hor = False
        has_ver = False
        
        for cfg in move_configs:
            m_prog = cfg['start'] + (cfg['end'] - cfg['start']) * progress
            # Map 0..100 to -0.5..0.5 (relative to slack)
            # Actually, let's map directly to pixels relative to center
            # 50% = 0 offset. 0% = -slack/2. 100% = +slack/2.
            factor = (m_prog - 50.0) / 100.0 # -0.5 to 0.5
            
            if cfg['dir'] == 'HOR':
                off_x += factor * slack_w
                has_hor = True
            elif cfg['dir'] == 'VER':
                # Inverted Y? usually 0 is top.
                # If we want 0% to be Top, then moving center UP means y decreases.
                # slack is positive. 
                # If we are at 0 (Top), center should be at h_orig/2 - slack/2 = min_y + h/2?
                # Let's stick to: 0 -> Top Edge, 100 -> Bottom Edge.
                off_y += factor * slack_h 
                has_ver = True

        # Apply default center-lock if no move defined for axis
        # (Already handled by 50% default in logic above effectively)

        # Shake Effect
        if shake:
            freq = 12.0
            intensity = float(shake_intensity if shake_intensity else 5)
            amp = intensity * 2.0 # Pixels
            off_x += np.sin(t * freq * 2 * np.pi) * amp
            off_y += np.cos(t * freq * 1.5 * np.pi) * amp

        # Calculate Center (Float)
        cx = (w_orig / 2.0) + off_x
        cy = (h_orig / 2.0) + off_y
        
        # v27.3: Sub-pixel Ken Burns using WarpAffine
        # This combines cropping and resizing into one sub-pixel accurate operation.
        # It eliminates "jitter" caused by integer rounding of coordinates.
        
        # Source Points (The crop rectangle in original image)
        # Top-Left, Top-Right, Bottom-Left
        src_pts = np.float32([
            [cx - curr_w / 2, cy - curr_h / 2],
            [cx + curr_w / 2, cy - curr_h / 2],
            [cx - curr_w / 2, cy + curr_h / 2]
        ])
        
        # Destination Points (The full target frame)
        dst_pts = np.float32([
            [0, 0],
            [target_w, 0],
            [0, target_h]
        ])
        
        try:
            # Compute Affine Transform Matrix
            M = cv2.getAffineTransform(src_pts, dst_pts)
            
            # Apply Warp (Crop + Resize + Subpixel Interpolation)
            # BORDER_CONSTANT ensures black bars if we are in FIT mode or go out of bounds
            resized = cv2.warpAffine(img_bgr, M, (target_w, target_h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0))
        except Exception as e:
            # Fallback (Safety net)
            print(f"Error in warpAffine: {e}")
            return np.zeros((target_h, target_w, 3), dtype=np.uint8)

        # Convert BGR to RGB
        return cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        
        # Resize to Target
        # INTER_LINEAR is fast and good for video. INTER_AREA better for downscaling static.
        # INTER_CUBIC is slower.
        # Given we want SPEED: Linear is standard.
        if crop.size == 0: return np.zeros((target_h, target_w, 3), dtype=np.uint8)
        
        resized = cv2.resize(crop, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
        
        # 4. Color Convert (BGR -> RGB)
        # MoviePy expects RGB
        return cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

    clip = VideoClip(make_frame, duration=duration)

    # ═══════════════════════════════════════════════════════════════════
    # ROTATE EFFECT (Post-Resize, usually fast enough via MoviePy or add to OpenCV?)
    # ═══════════════════════════════════════════════════════════════════
    if rotate:
        # Keeping existing rotate logic for now, usually less expensive than resize
        # or properly integrating into warpAffine if needed later.
        try:
           # ... (Reuse existing logic or simplified)
           # For safety/speed let's use the standard moviepy rotate for now
           # unless it proves slow.
             pass 
        except: pass

    # 3. OVERLAY PROCESSING (Only if needed)
    if overlay_path and os.path.exists(overlay_path):
        overlay = VideoFileClip(overlay_path, has_mask=True)
        if overlay.duration < duration:
            overlay = overlay.with_effects([vfx.Loop(duration=duration)])
        overlay = overlay.resized(target_size).subclipped(0, duration)
        overlay = overlay.with_mask(overlay.to_mask()).with_opacity(0.4).without_audio()
        return CompositeVideoClip([clip, overlay], size=target_size, bg_color=(0,0,0)).with_duration(duration)
    
    return clip.with_duration(duration)


def process_video_asset(video_path, duration, target_size, overlay_path=None, fit=None, clips_to_close=None, start_time=0.0, video_volume=0.0):
    """
    v14.0: Processes video with group-sync (start_time) and audio mixing (video_volume).
    """
    from moviepy import VideoFileClip, CompositeVideoClip, vfx, afx
    
    # Load video
    v_clip = VideoFileClip(video_path)
    if clips_to_close is not None: clips_to_close.append(v_clip)
    
    # Handle duration & sync: Loop if needed to cover the requested range
    required_end = start_time + duration
    if v_clip.duration < required_end:
        # Loop to ensure we can reach start_time + duration
        v_clip = v_clip.with_effects([vfx.Loop(duration=required_end + 1.0)])
    
    # Trim from start_time
    v_clip = v_clip.subclipped(start_time, required_end)
    logger.info(f"    🎬 [Debug] Video recortado. Duración: {v_clip.duration:.2f}s | Audio: {v_clip.audio is not None}")
    
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
    v_clip = v_clip.with_position("center")
    
    # Audio Logic
    try:
        # v15.8 UNIVERSAL AUDIO GUARD: Proactive integrity check for ALL assets
        if v_clip.audio:
            try:
                # 1. Test Read: Start of file
                v_clip.audio.to_soundarray(nbytes=2, buffersize=1000, fps=44100)
                
                # 2. Test Read: End of file (Common corruption point)
                if v_clip.duration > 1.0:
                    end_test = max(0, v_clip.duration - 0.5)
                    v_clip.audio.subclipped(end_test).to_soundarray(nbytes=2, fps=44100)
                    
            except Exception as e:
                logger.warning(f"  🔥 [CORRUPT AUDIO DETECTED]: {os.path.basename(video_path)} -> {e}. Stripping audio to save render.")
                v_clip = v_clip.without_audio()
                video_volume = 0.0
        else:
            logger.info(f"    ⚠️  El clip de video NO tiene pista de audio: {os.path.basename(video_path)}")

        video_volume = float(video_volume or 0.0)
        if video_volume > 0 and v_clip.audio:
             # v14.9: Force audio track retention before effects
             v_audio = v_clip.audio
             v_clip = v_clip.with_effects([afx.MultiplyVolume(video_volume)])
             # Re-attach audio if was lost during effect (MoviePy edge case)
             if not v_clip.audio and v_audio: v_clip = v_clip.with_audio(v_audio)
             logger.info(f"    🔊 [Audio] Volumen de activo aplicado: {video_volume} | Audio OK: {v_clip.audio is not None}")
        else:
             v_clip = v_clip.without_audio()
             
    except Exception as e:
        logger.warning(f"  ⚠️ [Audio Asset Error] Fallo general en asset {os.path.basename(video_path)}. Silenciando. Error: {e}")
        v_clip = v_clip.without_audio()
    
    layers = [v_clip]
    
    # Overlay support
    if overlay_path and os.path.exists(overlay_path):
        overlay = VideoFileClip(overlay_path, has_mask=True)
        if clips_to_close is not None: clips_to_close.append(overlay)
        if overlay.duration < duration:
            overlay = overlay.with_effects([vfx.Loop(duration=duration)])
        overlay = overlay.resized(target_size).subclipped(0, duration)
        overlay = overlay.with_mask(overlay.to_mask()).with_opacity(0.4).without_audio()
        layers.append(overlay)
        
    final_clip = CompositeVideoClip(layers, size=target_size, bg_color=(0,0,0)).with_duration(duration)
    if v_clip.audio:
        final_clip = final_clip.with_audio(v_clip.audio)
    return final_clip


# ═══════════════════════════════════════════════════════════════════
# Main Video Generation Function
# ═══════════════════════════════════════════════════════════════════
# v13.0: Progress Bridge for MoviePy (User Request)
class CacheProgressBarLogger(proglog.ProgressBarLogger):
    """
    Captures frame-level processing ("Items") and syncs them to Django Cache
    for real-time visibility in the terminal and UI.
    """
    def __init__(self, project_id):
        super().__init__()
        self.project_id = project_id
        from django.core.cache import cache
        self.cache = cache
        self.last_update = 0
        self.start_time = time.time()

    def bars_callback(self, bar, attr, value, old_value=None):
        # MoviePy uses 'chunk' for frames and 't' for general progress
        if bar in ['chunk', 't']:
            now = time.time()
            if now - self.last_update > 0.5: # 2Hz refresh
                self.last_update = now
                total = self.bars.get(bar, {}).get('total', 1)
                # Map rendering (the final phase) to 90-100% range
                p_val = 90 + (value / total * 10) if total > 0 else 90
                
                elapsed = now - self.start_time
                speed = value / elapsed if elapsed > 0 else 0
                
                status_text = f"Item {value}/{total} ({p_val:.1f}%) | {speed:.2f} its/s"
                self.cache.set(f"project_{self.project_id}_progress", p_val, timeout=60)
                self.cache.set(f"project_{self.project_id}_status_text", status_text, timeout=60)

def render_pro_subtitles(text, duration, target_size, active_word_index=None, full_highlight=False, word_timings=None, is_dynamic=False, y_position=0.70, is_highlight=False):
    """
    v16.5 PRO: Modular Premium Subtitle Renderer.
    - full_highlight: If True, the entire block is Neon Yellow (Movie Mode).
    - word_timings: List of {start, end, word} for high-precision Shorts mode.
    - is_dynamic: Triggers logic for progressive word appearance.
    - y_position: Vertical position (0.0-1.0), default 0.70. v17.0: Enables dual-layer (highlight/karaoke).
    - is_highlight: v18.1: Emphatic highlight [PHO:h] mode (Yellow on Black Box).
    """
    from moviepy import TextClip, ColorClip, CompositeVideoClip, vfx
    
    # 1. Config & Font Robustness
    try:
        font_list = TextClip.list('font')
        font = 'Arial-Bold' if 'Arial-Bold' in font_list else ('Arial' if 'Arial' in font_list else 'C:/Windows/Fonts/arialbd.ttf')
    except:
        font = 'C:/Windows/Fonts/arialbd.ttf' if os.path.exists('C:/Windows/Fonts/arialbd.ttf') else 'C:/Windows/Fonts/arial.ttf'
    
    # v17.2.13: Standard Width (85% of screen)
    standard_width = int(target_size[0] * 0.85)
    fontsize = int(target_size[1] * 0.05) if (is_dynamic or is_highlight) else int(target_size[1] * 0.045)
    
    # v17.0: Customizable vertical position for dual-layer rendering
    y_pos = int(target_size[1] * y_position)
    
    # Base Color Logic
    highlight_color = '#FFFF00' # Neon Yellow
    # v19.1: Platinum Grey (#D1D1D1) for a more cinematic look
    base_color = highlight_color if (full_highlight or is_highlight) else '#D1D1D1'
    stroke_color = '#000000'
    bg_color = 'black' if is_highlight else None 
    
    # v27.3: Dynamic Wrap Limit based on orientation
    wrap_limit = 20 if target_size[0] < target_size[1] else 35

    def wrap_text(t, max_chars=30): 
        words = t.split()
        lines = []
        current_line = []
        for w in words:
            if len(' '.join(current_line + [w])) <= max_chars:
                current_line.append(w)
            else:
                lines.append(' '.join(current_line))
                current_line = [w]
        if current_line:
            lines.append(' '.join(current_line))
        return '\n'.join(lines)

    if is_dynamic and word_timings:
        # ... [Karaoke Logic truncated for this edit] ...
        # ═══════════════════════════════════════════════════════════════════
        # [MODE: DYN] Karaoke Stretchy-Mask (v16.7.13) - Phonetic Support
        # ═══════════════════════════════════════════════════════════════════
        # v17.3.3: Sincronizado con avgl_engine (10 palabras)
        sub_clips = []
        chunk_size = 10
        
        # v16.7.13: Vertical clearance
        safe_h_composite = int(fontsize * 3.0) 
        
        def create_safe_text_clip(word, color, duration):
            try:
                temp = TextClip(text=f" {word} ", font_size=fontsize, font=font, method='label')
                w_measured = temp.w; temp.close()
            except:
                w_measured = int(fontsize * len(word) * 0.55)

            return TextClip(
                text=word,
                font_size=fontsize,
                color=color,
                stroke_color=stroke_color,
                stroke_width=2.5,
                font=font,
                method='caption',
                size=(w_measured, safe_h_composite),
                text_align='center',
                vertical_align='center',
                bg_color=(0, 0, 0, 0)
            ).with_duration(duration)

        # v17.1: Preprocess text to handle padding placeholders and escapes
        # 1. Replace escaped underscores (\\_) with a temporary token
        text_processed = text.replace("\\_", "<<<UNDERSCORE>>>")
        # 2. Filter out standalone _ placeholders (padding tokens)
        words_raw = text_processed.split()
        words_filtered = [w for w in words_raw if w != "_"]
        # 3. Restore escaped underscores
        words_final = [w.replace("<<<UNDERSCORE>>>", "_") for w in words_filtered]
        # 4. Rejoin
        text_clean = " ".join(words_final)
        
        # source of truth for display (after filtering)
        visible_words_all = text_clean.split()
        
        for i in range(0, len(visible_words_all), chunk_size):
            chunk_visible = visible_words_all[i : i + chunk_size]
            chunk_phrase = " ".join(chunk_visible)
            if not chunk_phrase: continue
            
            # Map chunk to timings
            chunk_start_idx = i
            chunk_end_idx = i + len(chunk_visible)
            relevant_t = word_timings[chunk_start_idx : chunk_end_idx]
            
            if relevant_t:
                chunk_start = relevant_t[0].get('start', 0)
                chunk_end = relevant_t[-1].get('end', chunk_start + 0.5)
            else:
                chunk_start = 0; chunk_end = duration
            
            chunk_duration = chunk_end - chunk_start
            if chunk_duration <= 0: chunk_duration = 0.5

            # 1. Create the BASE phrase (White)
            # v16.7.17: Precise width measurement for centering
            try:
                temp_p = TextClip(text=chunk_phrase, font_size=fontsize, font=font, method='label')
                chunk_width = temp_p.w; temp_p.close()
            except:
                chunk_width = int(fontsize * len(chunk_phrase) * 0.5)

            base_phrase_clip = create_safe_text_clip(chunk_phrase, base_color, chunk_duration)
            
            # v17.2.13: Use standard width container for consistent alignment
            chunk_offset_x = (standard_width - chunk_width) // 2
            chunk_clips = [base_phrase_clip.with_position((chunk_offset_x, 0))]
            
            # 2. Layer individual yellow highlights
            for word_idx, w_info in enumerate(relevant_t):
                word_text = w_info.get('word', '').strip()
                if not word_text: continue
                
                # v16.7.17: Precise prefix measurement for perfect alignment
                prefix_words = chunk_visible[:word_idx]
                prefix_text = " ".join(prefix_words) + " " if prefix_words else ""
                try:
                    temp_p = TextClip(text=prefix_text, font_size=fontsize, font=font, method='label')
                    x_in_chunk = temp_p.w; temp_p.close()
                except:
                    x_in_chunk = int(fontsize * len(prefix_text) * 0.5)


                w_high_dur = w_info.get('end', 0) - w_info.get('start', 0)
                if w_high_dur <= 0: w_high_dur = 0.1
                
                # v17.2: Adelantar 200ms para sincronización óptima
                w_high_start_rel = max(0, w_info.get('start', 0) - chunk_start - 0.20)
                
                # Create the highlight clip
                w_high_full = create_safe_text_clip(word_text, highlight_color, w_high_dur)
                
                # Position relative to base phrase
                # v16.7.19: Raise yellow highlight by 4px for perfect alignment
                chunk_clips.append(w_high_full.with_start(w_high_start_rel).with_position((chunk_offset_x + x_in_chunk, -4)))

            
            # 3. Composite as a Wide Strip (target_size[0] width)
            # v16.7.17: This ensures no clip mask is ever outside the boundary, preventing broadcast errors
            # 3. Composite with Standard Width (v17.2.13)
            # This ensures all blocks have the same horizontal origin/centering
            chunk_comp = CompositeVideoClip(chunk_clips, size=(standard_width, safe_h_composite), bg_color=None)
            sub_clips.append(chunk_comp.with_start(chunk_start))
                
        if not sub_clips: return None
        
        # Center the whole sub-strip based on standard_width
        final_x = (target_size[0] - standard_width) // 2
        return CompositeVideoClip(sub_clips, size=(target_size[0], safe_h_composite), bg_color=None).with_duration(duration).with_position((final_x, y_pos - 2))

    else:
        # v19.1: Universal Anti-Clipping for Standard Subs
        # We use an oversized height (1.5x) to ensure strokes/descenders are safe.
        # This prevents the "cut" reported by the Arquitecto.
        t_height_universal = int(fontsize * 1.5)
        
        # Mode Logic
        if is_highlight:
            # v27.3: Enable wrapping for Titles
            text = wrap_text(text, max_chars=wrap_limit)
            line_count = len(text.split('\n'))

            # 1. Detect natural width first (v18.6)
            temp_t = TextClip(text=text, font_size=fontsize, font=font, method='label')
            natural_w = temp_t.w
            temp_t.close()

            # 2. Create text with DYNAMIC height (v27.3)
            # v18.6 base was 2.5x. Now we scale by lines.
            t_height = int(fontsize * 1.5 * line_count) + int(fontsize * 1.0)
            t_width = min(standard_width, natural_w + int(fontsize * 0.5)) 
            
            t_clip = TextClip(
                text=text,
                font_size=fontsize,
                color=base_color,
                stroke_color=stroke_color,
                stroke_width=3.0,
                font=font,
                method='caption',
                size=(t_width, t_height)
            ).with_duration(duration)

            # 3. Create a background box
            bg_w = t_clip.w + int(fontsize * 1.5)
            bg_h = t_height 
            
            bg_clip = ColorClip(size=(bg_w, bg_h), color=(0,0,0)).with_duration(duration)
            
            # 4. Composite text on background (centered)
            final_clip = CompositeVideoClip([
                bg_clip,
                t_clip.with_position('center')
            ], size=(bg_w, bg_h)).with_duration(duration)
            
            # Position logic: Center horizontally, use specific y_pos
            final_clip = final_clip.with_position(('center', y_pos))
            
        else:
            # v27.3: Dynamic wrap for standard subs too
            text = wrap_text(text, max_chars=wrap_limit)
            line_count = len(text.split('\n'))
            t_height_dynamic = int(fontsize * 1.4 * line_count) + int(fontsize * 0.5)

            # v19.1: Universal Anti-Clipping for Standard Subs
            final_clip = TextClip(
                text=text,
                font_size=fontsize,
                color=base_color,
                stroke_color=stroke_color,
                stroke_width=3.0,
                font=font,
                method='caption',
                size=(standard_width, t_height_dynamic), 
                text_align='center'
            ).with_duration(duration)
            
            # Position: Center horizontally
            final_clip = final_clip.with_position(((target_size[0] - standard_width) // 2, y_pos))
        
        return final_clip

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
    
    # v26.0: Global Subtitle Collection
    all_srt_items = []
    video_base_cursor = 0.0
    
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
        project.save(update_fields=['status'])
        
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
            project.title = script.title; project.save(update_fields=['title'])

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
            
            # v13.5.5: Professional Audio Normalization (Stereo Force & Validation)
            base_audio_name = f"project_{project.id}_scene_{i:03d}"
            audio_path = os.path.join(temp_audio_dir, f"{base_audio_name}.mp3")
            
            # Custom Audio Priority
            if scene.audio:
                custom_audio_path = os.path.join(assets_dir, scene.audio)
                if not os.path.exists(custom_audio_path): custom_audio_path = os.path.join(settings.MEDIA_ROOT, scene.audio)
                
                if os.path.exists(custom_audio_path):
                    logger.log(f"    🔊 Normalizando audio personalizado: {os.path.basename(custom_audio_path)}")
                    
                    # Force normalization via FFmpeg (Fixes Duration: N/A from browsers)
                    try:
                        import subprocess
                        # Find FFmpeg binary path robustly
                        ffmpeg_exe = 'ffmpeg'
                        try:
                            import imageio_ffmpeg
                            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
                        except ImportError: pass
                        
                        # Convert to standard MP3 to ensure valid headers and duration
                        # v13.5.5: Force -ac 2 (Stereo) to prevent mixing issues with background music
                        cmd = [
                            ffmpeg_exe, '-y', '-i', custom_audio_path,
                            '-af', 'volume=1.5',
                            '-ac', '2',
                            '-codec:a', 'libmp3lame', '-qscale:a', '2',
                            audio_path
                        ]
                        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
                        
                        if not os.path.exists(audio_path) or os.path.getsize(audio_path) < 100:
                             raise Exception(f"Archivo de audio normalizado inválido o muy pequeño: {os.path.getsize(audio_path) if os.path.exists(audio_path) else 0} bytes")
                        
                        temp_clip = AudioFileClip(audio_path)
                        logger.log(f"    📏 Normalizado OK: {temp_clip.duration:.2f}s | {os.path.getsize(audio_path)//1024}KB")
                        
                        audio_files.append((scene, audio_path))
                        audio_durations[scene] = temp_clip.duration
                        temp_clip.close()
                        continue
                    except subprocess.CalledProcessError as e:
                        logger.log(f"    ❌ Fallo crítico FFmpeg normalization: {e.stderr}")
                        import shutil; shutil.copy2(custom_audio_path, audio_path)
                        audio_files.append((scene, audio_path))
                        audio_durations[scene] = 1.0
                        continue
                    except Exception as e:
                        logger.log(f"    ⚠️ Error en normalización FFmpeg: {e}")
                        import shutil; shutil.copy2(custom_audio_path, audio_path)
                        audio_files.append((scene, audio_path))
                        audio_durations[scene] = 1.0
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
            project.status = 'error'
            project.save(update_fields=['status'])
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

        # v12.5: Granular Progress & Speed Logging (Cache-First)
        # Pre-calculate total scenes for accurate progress bar
        total_scenes = sum(len(b.scenes) for b in script.blocks)
        global_scene_cnt = 0
        process_start_time = time.time()
        
        from django.core.cache import cache
        # v12.5.3: Register active project for global terminal logging
        cache.set("active_rendering_project_id", project.id, timeout=3600)

        for b_idx, block in enumerate(script.blocks):
            # Legacy Block-based progress removed in favor of granular scene progress
            # kept only for debug log
            logger.log(f"📦 Procesando Bloque {b_idx+1}: {block.title}")
            block_scene_clips = []
            block_voice_intervals = []
            block_cursor = 0.0
            
            for s_idx, scene in enumerate(block.scenes):
                # Granular Progress Update
                global_scene_cnt += 1
                
                # Calculate metrics
                elapsed = time.time() - process_start_time
                speed = global_scene_cnt / elapsed if elapsed > 0 else 0
                
                # Map progress to 35% - 85% range
                p_val = 35 + (global_scene_cnt / total_scenes * 50)
                
                # v12.5.1: Hybrid Status Caching (Progress + Text)
                # v13.0 Terminology: Item (User Request)
                status_text = f"Item {global_scene_cnt}/{total_scenes} ({p_val:.1f}%) | {speed:.2f} its/s"
                cache.set(f"project_{project.id}_progress", p_val, timeout=60)
                cache.set(f"project_{project.id}_status_text", status_text, timeout=60)
                
                # Log to console
                logger.log(f"  ⏳ {status_text}")

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
                    # v14.3 Improvement: Silent fallback has 0 duration to let 'pause' rule
                    audio_clip = None 
                
                # v14.3: Duration is voice + pause. If no voice, it's just pause.
                voice_duration = audio_clip.duration if audio_clip else 0.0
                
                try: s_pause = float(scene.pause or 0.0)
                except: s_pause = 0.0
                duration = voice_duration + s_pause
                
                if duration <= 0:
                    duration = 1.0 # Minimal failsafe
                
                # ASSET LOADING & FALLBACK
                clip = None
                # v16.7.20: Filter out empty assets to treat them like no-assets (fast mode)
                # v16.7.21: Also filter out generic category placeholders ('image', 'video', etc.)
                def is_valid_asset(a):
                    asset_id = (getattr(a, 'id', '') or getattr(a, 'type', '') or '').strip()
                    if not asset_id:
                        return False
                    if asset_id.lower() in ['video', 'image', 'none', 'null']:
                        return False
                    return True
                
                valid_assets = [a for a in scene.assets if is_valid_asset(a)]
                if valid_assets:
                    asset = valid_assets[0]
                    # v14.7 Fix: Prioritize ID over Type to avoid 'video'/'image' string leaks
                    # getattr(asset, 'id') should be the real filename or absolute path.
                    raw_path = str(getattr(asset, 'id', '') or getattr(asset, 'type', '') or "").strip()
                        
                    asset_path = None
                    
                    # 1. Check Absolute Path (Priority)
                    norm_path = os.path.normpath(raw_path)
                    if norm_path and os.path.isabs(norm_path) and os.path.isfile(norm_path):
                         asset_path = norm_path
                         logger.log(f"    ✅ Ruta ABSOLUTA detectada y validada: {os.path.basename(asset_path)}")
                         logger.log(f"       Path: {asset_path}")
                    else:
                        # 2. Legacy Relative Logic (Fallback)
                        fname = raw_path
                        if '://' in fname or ':\\' in fname or '/media/' in fname:
                             fname = os.path.basename(fname)
                        
                        # Search in multiple potential directories
                        search_dirs = [
                            assets_dir,
                            os.path.join(settings.MEDIA_ROOT, 'videos'),
                            os.path.join(settings.MEDIA_ROOT, 'uploads'),
                            os.path.join(settings.MEDIA_ROOT, 'outputs')
                        ]
                        
                        found_path = None
                        for s_dir in search_dirs:
                            test_path = os.path.join(s_dir, fname)
                            if os.path.isfile(test_path):
                                found_path = test_path
                                break
                            # Try extensions
                            for ext in ['.png', '.jpg', '.jpeg', '.mp4']:
                                if os.path.isfile(test_path + ext):
                                    found_path = test_path + ext
                                    break
                            if found_path: break
                        
                        asset_path = found_path if found_path else os.path.join(assets_dir, fname)
                    
                    # LOG RESULT
                    if os.path.isfile(asset_path):
                        if not os.path.isabs(raw_path):
                            logger.log(f"    ✅ Asset encontrado en media/assets: {os.path.basename(asset_path)}")
                    else:
                        logger.log(f"    ❌ Asset NO encontrado o es directorio: '{raw_path}'")
                        logger.log(f"       Buscado en: {asset_path}")

                    if not os.path.isfile(asset_path):
                        logger.log(f"    🔍 Buscando respaldo (fallback)...")
                        # Smart Fallback
                        fallback_candidates = [
                            os.path.join(assets_dir, "notiaci_intro_wide.png"), 
                            os.path.join(assets_dir, "banner_notiaci.png")
                        ]
                        found_fb = False
                        for fb in fallback_candidates:
                            if os.path.exists(fb): 
                                asset_path = fb
                                found_fb = True
                                logger.log(f"    💡 Respaldo estándar encontrado: {os.path.basename(asset_path)}")
                                break
                        
                        if not found_fb:
                            try:
                                any_imgs = [f for f in os.listdir(assets_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                                if any_imgs: 
                                    asset_path = os.path.join(assets_dir, any_imgs[0])
                                    found_fb = True
                                    logger.log(f"    💡 Respaldo aleatorio encontrado: {os.path.basename(asset_path)}")
                            except: pass
                        
                        if not found_fb:
                            from moviepy import ColorClip
                            clip = ColorClip(size=target_size, color=(0,0,0), duration=duration)
                            logger.log("    🛑 SIN ASSETS DISPONIBLES. Usando fondo negro.")
                        else:
                            # Apply fallback
                            clip = apply_ken_burns(asset_path, duration, target_size, zoom="1.1:1.0", move="HOR:50:50")
                            clips_to_close.append(clip)
                    
                    if not clip and os.path.isfile(asset_path):
                        # Determine Asset Type (Image vs Video)
                        is_video = asset_path.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm'))
                        
                        # ═══════════════════════════════════════════════════════════════════
                        # MASTER SHOT / GROUP INTERPOLATION & V5.0 EFFECTS
                        eff_zoom = asset.zoom or "1.0:1.3"
                        eff_move = asset.move or "HOR:50:50"
                        eff_shake = getattr(asset, 'shake', False)
                        eff_shake_intensity = getattr(asset, 'shake_intensity', 5)
                        eff_rotate = getattr(asset, 'rotate', None)

                        # v14.2 OPTIMIZATION: Videos don't need Zoom/Move math
                        if is_video:
                            eff_zoom = "1.0"
                            eff_move = "HOR:50:50"
                            logger.log(f"    📽️ Video detectado: Omitiendo efectos de Zoom/Move.")
                        else:
                        
                            # v5.0 Directional Aliases (Extended Support)
                            MOVE_ALIASES = {
                                "UP": "VER:100:0",
                                "DOWN": "VER:0:100",
                                "LEFT": "HOR:100:0",
                                "RIGHT": "HOR:0:100",
                                "CENTER": "HOR:50:50"
                            }
                            
                            raw_move = str(eff_move).strip().upper()
                            if raw_move in MOVE_ALIASES:
                                eff_move = MOVE_ALIASES[raw_move]
                            
                            # v5.0 Parsing: Extract SHAKE/ROTATE from eff_move if present
                            if eff_move and 'SHAKE' in eff_move.upper():
                                match = re.search(r'SHAKE:(\d+)', eff_move, re.IGNORECASE)
                                eff_shake = True
                                if match: eff_shake_intensity = int(match.group(1))
                            
                            if eff_move and 'ROTATE' in eff_move.upper():
                                match = re.search(r'ROTATE:([-0-9.]+):([-0-9.]+)', eff_move, re.IGNORECASE)
                                if match: eff_rotate = f"{match.group(1)}:{match.group(2)}"
                                else:
                                    match_static = re.search(r'ROTATE:([-0-9.]+)', eff_move, re.IGNORECASE)
                                    if match_static: eff_rotate = match_static.group(1)
                            
                            if scene.group_id and scene.group_settings:
                                g = scene.group_settings
                                g_zoom = g.get("zoom", "1.0:1.3")
                                g_move = g.get("move", "HOR:50:50")
                                
                                try:
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
                                    gz_start = safe_float(z_parts[0], 1.0); gz_end = safe_float(z_parts[1], 1.3)
                                    
                                    z_s = gz_start + (gz_end - gz_start) * (start_in_group / total_group_duration)
                                    z_e = gz_start + (gz_end - gz_start) * ((start_in_group + duration) / total_group_duration)
                                    eff_zoom = f"{z_s:.3f}:{z_e:.3f}"
                                    
                                    # Interpolate Move (Simple Linear)
                                    m_configs = []
                                    if '+' in g_move:
                                        for p in [p.strip() for p in g_move.split('+')]:
                                            mp = p.split(':')
                                            if len(mp) >= 3: m_configs.append({'dir': mp[0], 's': safe_float(mp[1], 50.0), 'e': safe_float(mp[2], 50.0)})
                                    else:
                                        mp = g_move.split(':')
                                        if len(mp) >= 3: m_configs.append({'dir': mp[0], 's': safe_float(mp[1], 50.0), 'e': safe_float(mp[2], 50.0)})
                                    
                                    for cfg in m_configs:
                                        ms = cfg['s']; me = cfg['e']
                                        m_s = ms + (me - ms) * (start_in_group / total_group_duration)
                                        m_e = ms + (me - ms) * ((start_in_group + duration) / total_group_duration)
                                        if cfg['dir'] == 'HOR':
                                            eff_move = f"HOR:{m_s:.1f}:{m_e:.1f}" if not eff_move or '+' not in eff_move else eff_move + f" + HOR:{m_s:.1f}:{m_e:.1f}"
                                        else:
                                            eff_move += f" + VER:{m_s:.1f}:{m_e:.1f}" if eff_move else f"VER:{m_s:.1f}:{m_e:.1f}"
                                except Exception as e:
                                    logger.log(f"    ⚠️ Error en interpolación visual de grupo: {e}")
                                    eff_zoom = "1.0:1.3"; eff_move = "HOR:50:50"

                        logger.log(f"  🎬 Item {s_idx+1}: {os.path.basename(asset_path)} | Zoom: {eff_zoom} | Move: {eff_move}")
                        
                        # Overlay
                        overlay_path = None
                        if asset.overlay:
                            overlay_path = os.path.join(overlay_dir, f"{asset.overlay}.mp4")
                            if not os.path.exists(overlay_path): overlay_path = None
                        
                        # v14.0 Sync Logic: Identify timing for groups
                        sync_start_time = 0.0
                        if scene.group_id:
                            # Re-use calculated start_in_group if it exists (K-Burns logic above)
                            # or calculate it here
                            group_scenes = [s for s in all_scenes if s.group_id == scene.group_id]
                            for s in group_scenes:
                                if s == scene: break
                                s_dur = audio_durations.get(s, 1.0) + s.pause
                                sync_start_time += s_dur

                        if is_video:
                            # v14.9: Smart Default - If not specified, we assume user wants sound (Cinema Mode)
                            raw_v_vol = getattr(asset, 'video_volume', None)
                            v_vol = float(raw_v_vol) if raw_v_vol is not None else 1.0
                            
                            # v15.2: Explicit Cinema mode (Auto-Persistence)
                            is_cinema = getattr(asset, 'cinema_mode', False)
                            
                            if is_cinema and voice_duration < 1.0:
                                try:
                                    from moviepy import VideoFileClip
                                    temp_v = VideoFileClip(asset_path)
                                    if temp_v.duration > duration:
                                        logger.log(f"    🎬 [MODO CINE] Auto-Persistencia Activada: {duration:.2f}s -> {temp_v.duration:.2f}s")
                                        duration = temp_v.duration
                                    temp_v.close()
                                except Exception as e:
                                    logger.log(f"    ⚠️ Error en Auto-Persistencia: {e}")

                            logger.log(f"  📽️ Asset detectado como VÍDEO (v14.0): {os.path.basename(asset_path)} | Sync: {sync_start_time:.2f}s | Vol: {v_vol}")
                            
                            # v15.0: Fast Assembly Check
                            is_fast = getattr(asset, 'fast_assembly', False)
                            
                            if is_fast and not overlay_path:
                                # v15.5: Pure Fast Path (Direct Copy for Master Assembly)
                                if not audio_clip and v_vol == 1.0 and is_cinema:
                                    logger.log(f"    🚀 [FastAssembly] MODO ENSAMBLAJE PURO: Copia directa de {os.path.basename(asset_path)}")
                                    clip = VideoFileClip(asset_path)
                                    if clips_to_close is not None: clips_to_close.append(clip)
                                    if clip.size != target_size: clip = clip.resized(target_size)
                                    is_fast_success = True
                                else:
                                    logger.log(f"    ⚡ [FastAssembly] Modo Inyección Directa Activado para: {os.path.basename(asset_path)}")
                                    # 1. Prepare scene audio (Voice or Silence)
                                    temp_scene_audio = os.path.join(temp_audio_dir, f"fast_audio_{s_idx}.aac")
                                    
                                    if audio_clip:
                                        audio_clip.write_audiofile(temp_scene_audio, logger=None)
                                    else:
                                        # Inyectar silencio de la duración de la escena
                                        logger.log(f"    🔇 Inyectando silencio de {duration:.2f}s para inyección directa.")
                                        from moviepy import AudioClip
                                        silent_audio = AudioClip(lambda t: 0, duration=duration)
                                        silent_audio.write_audiofile(temp_scene_audio, fps=44100, logger=None)
                                        silent_audio.close()
                                    
                                    # 2. Mux
                                    temp_scene_video = os.path.join(temp_audio_dir, f"fast_scene_{s_idx}.mp4")
                                    success = fast_mux_audio_video(asset_path, temp_scene_audio, temp_scene_video, video_volume=v_vol if audio_clip else 0.0)
                                    
                                    if success:
                                        from moviepy import VideoFileClip
                                        clip = VideoFileClip(temp_scene_video)
                                        if clips_to_close is not None: clips_to_close.append(clip)
                                        if clip.size != target_size: clip = clip.resized(target_size)
                                        is_fast_success = True
                                    else:
                                        logger.log(f"    ⚠️ Falló FastAssembly. Reintentando con renderizado estándar.")
                                        is_fast_success = False
                                
                                if not is_fast_success:
                                    is_fast = False # Fallback to standard
                                    
                            if not is_fast or overlay_path:
                                clip = process_video_asset(
                                    asset_path, duration, target_size,
                                    overlay_path=overlay_path,
                                    fit=asset.fit,
                                    clips_to_close=clips_to_close,
                                    start_time=sync_start_time,
                                    video_volume=v_vol
                                )
                        else:
                            # Apply Ken Burns (Standard image logic)
                            clip = apply_ken_burns(
                                asset_path, duration, target_size,
                                zoom=eff_zoom,
                                move=eff_move,
                                overlay_path=overlay_path, 
                                fit=asset.fit,
                                shake=eff_shake,
                                shake_intensity=eff_shake_intensity,
                                rotate=eff_rotate,
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
                                # v15.7: Force float cast to prevent numpy ufunc error (dtype <U3)
                                vol_safe = float(sfx_item.volume)
                                s_clip = AudioFileClip(sfx_path).with_effects([afx.MultiplyVolume(vol_safe)])
                                if clips_to_close is not None: clips_to_close.append(s_clip)
                                
                                # AVGL v4: Offset is word-based. 
                                # Calculate delay: (scene_audio_duration / scene_word_count) * offset
                                delay = 0
                                sfx_offset = int(sfx_item.offset or 0)
                                if sfx_offset > 0 and audio_clip:
                                    # Count words in scene text
                                    clean_text = re.sub(r'\[.*?\]', '', scene.text)
                                    words = clean_text.split()
                                    if words:
                                        delay = (audio_clip.duration / len(words)) * sfx_item.offset
                                
                                scene_sfx_clips.append(s_clip.with_start(delay).with_duration(min(s_clip.duration, duration - delay)))
                                logger.log(f"    🔊 SFX: {os.path.basename(sfx_path)} (vol: {vol_safe}, offset: {sfx_item.offset} words -> {delay:.2f}s)")
                            except Exception as e:
                                logger.log(f"    ⚠️ Error SFX {sfx_item.type}: {e}")

                # Mix Scene Audio (Voice + SFX)
                if scene_sfx_clips:
                    final_scene_audio = CompositeAudioClip([audio_clip] + scene_sfx_clips)
                    audio_clip = final_scene_audio

                # SUBTITLE RENDERING (Modular v16.0)
                sub_clips_dynamic = []
                try:
                    if hasattr(scene, 'subtitles') and scene.subtitles:
                        # v17.2.1: CRITICAL FIX - Use full duration (voice + pause) for timing
                        # Previously used only voice_duration, causing subtitle desync with scene pauses
                        timing_base = duration  # duration already = voice_duration + scene.pause (line 781)
                        # v16.7.12: Unified Word Count (Clean text to match TTS output)
                        # v16.7.23: Professional subtitle standards (Netflix/HBO)
                        MIN_READING_SPEED = 2.6  # palabras/segundo (estándar profesional)
                        MIN_SUBTITLE_DURATION = 1.0  # segundos
                        MAX_SUBTITLE_DURATION = 7.0  # segundos
                        
                        clean_scene_text = re.sub(r'\[.*?\]', '', scene.text)
                        total_words_scene = len(clean_scene_text.split())
                        
                        for idx, sub_data in enumerate(scene.subtitles):
                            s_text = sub_data.get('text', '')
                            s_offset = sub_data.get('offset', 0)
                            s_w_count = sub_data.get('word_count', 4)
                            phonetic_count = sub_data.get('phonetic_count', s_w_count)  # v17.0: Phonetic mapping
                            is_highlight = sub_data.get('is_highlight', False)           # v17.0: Highlight mode
                            y_pos = sub_data.get('y_position', 0.70)                     # v17.0: Vertical position (v17.2.10: Moved up to 0.70)
                            is_dynamic = sub_data.get('is_dynamic', False)
                            is_movie_mode = sub_data.get('movie_mode', False)
                            
                            # v26.0: Collect for Post-Injection (Absolute Timing)
                            # Timing must be: Global Cursor (completed blocks) + Block Cursor (previous scenes in current block) + local timing
                            s_start_global_base = video_base_cursor + block_cursor
                            
                            if not s_text or s_w_count < 0: continue
                            
                            # v17.0: Enhanced timing logic with phonetic consolidation
                            relevant_timings = None
                            consolidated_timing = None
                            
                            # v18.9: Support word timings for ALL subtitles (Dynamic or Static) if available
                            if hasattr(scene, 'word_timings') and scene.word_timings:
                                # Extract timings using phonetic_count (not word_count)
                                relevant_timings = scene.word_timings[s_offset : s_offset + phonetic_count]
                                
                                # v17.0: Consolidate if phonetic words > display words
                                if phonetic_count > s_w_count and len(relevant_timings) > 0:
                                    # Multiple phonetic words → Single display text
                                    consolidated_timing = {
                                        'word': s_text,
                                        'start': relevant_timings[0]['start'],
                                        'end': relevant_timings[-1]['end']
                                    }
                                    s_start = consolidated_timing['start']
                                    s_dur = consolidated_timing['end'] - s_start
                                    logger.log(f"      [PHO] Consolidated {phonetic_count}p → 1d: \"{s_text}\" ({s_dur:.2f}s)")
                                elif len(relevant_timings) > 0:
                                    # v18.9: Perfect sync for static/header subs using phonetic_count
                                    s_start = relevant_timings[0]['start']
                                    s_dur = relevant_timings[-1]['end'] - s_start
                                    
                                    # v17.2.8: Advance highlight clips by 200ms
                                    if is_highlight:
                                        s_start = max(0, s_start - 0.20)
                                else:
                                    # Fallback if slice resulted in empty timings
                                    s_start = 0
                                    s_dur = 1.5
                            else:
                                # Fallback: distribución uniforme con mínimo legible
                                s_start = (s_offset / total_words_scene) * timing_base if total_words_scene > 0 else 0
                                
                                # Calcular duración proporcional usando phonetic_count
                                proportional_dur = (phonetic_count / total_words_scene) * timing_base if total_words_scene > 0 else 1.5
                                
                                # Calcular duración mínima legible basada en estándar profesional
                                min_legible_dur = s_w_count / MIN_READING_SPEED
                                
                                # Usar el mayor entre proporcional y mínimo legible
                                s_dur = max(proportional_dur, min_legible_dur)
                                
                                # Aplicar límites min/max
                                s_dur = max(MIN_SUBTITLE_DURATION, min(MAX_SUBTITLE_DURATION, s_dur))
                            
                            s_start = min(s_start, duration - 0.1)
                            s_dur = max(0.1, min(s_dur, duration - s_start))
                            
                            # Alignment logic (SRT tags: {\an8} Top, {\an2} Bottom)
                            align_tag = "{\\an8}" if y_pos < 0.6 else "{\\an2}"
                            
                            # v26.1: Populate all_srt_items (now used for ASS) with full metadata
                            
                            # v26.9: Karaoke Phonetic -> Visual Mapping
                            # Fixes issue where [DYN] shows TTS phonetic text instead of visual text.
                            final_timings = relevant_timings
                            if is_dynamic and relevant_timings:
                                v_words = s_text.split()
                                p_words = relevant_timings
                                
                                if len(v_words) == len(p_words):
                                    # 1:1 Match - Perfect Swap
                                    final_timings = []
                                    for i, w_obj in enumerate(p_words):
                                        new_obj = w_obj.copy()
                                        new_obj['word'] = v_words[i]
                                        final_timings.append(new_obj)
                                else:
                                    # Mismatch - Proportional Distribution (Fallback)
                                    # Example: [PHO]veintidos|22[/PHO] -> 1 visual, 1 phonetic ("veintidos")
                                    # Example: [PHO]veintidos de enero|22/01[/PHO] -> 1 visual, 3 phonetic
                                    logger.log(f"      [DYN] Mismatch: {len(v_words)}v vs {len(p_words)}p. Remapping...")
                                    
                                    start_t = p_words[0]['start']
                                    end_t = p_words[-1]['end']
                                    total_dur = end_t - start_t
                                    total_chars = sum(len(w) for w in v_words)
                                    if total_chars == 0: total_chars = 1 # Safety
                                    
                                    final_timings = []
                                    curr_t = start_t
                                    for w in v_words:
                                        # Calculate duration based on character length ratio
                                        w_dur = (len(w) / total_chars) * total_dur
                                        final_timings.append({
                                            'word': w,
                                            'start': curr_t,
                                            'end': curr_t + w_dur
                                        })
                                        curr_t += w_dur
                            
                            # v26.11: GLOBAL KARAOKE COMPENSATOR
                            # "Audio Ferrari" Fix: Shift all visuals -80ms to catch up with audio.
                            # This covers system latency and MP3 start gaps.
                            if is_dynamic and final_timings:
                                sync_offset = -0.08
                                for wt in final_timings:
                                    wt['start'] = max(0.0, wt['start'] + sync_offset)
                                    wt['end'] = max(0.0, wt['end'] + sync_offset)
                                
                                # Update S_START to match new timings (Critical!)
                                if final_timings:
                                    s_start = final_timings[0]['start']
                                    s_dur = final_timings[-1]['end'] - s_start

                            metadata = {
                                'text': s_text,
                                'start': s_start_global_base + s_start,
                                'end': s_start_global_base + s_start + s_dur,
                                'is_dynamic': is_dynamic,
                                'y_pos': y_pos,
                                'relevant_timings': final_timings if is_dynamic else None
                            }
                            all_srt_items.append(metadata)
                            
                            # v17.2.9: TEMPORARY - Disable yellow karaoke highlights for MoviePy (we only use FFmpeg now)
                            # We keep the DYN timing but render as static white subtitles for visual cleanup
                            d_txt_clip = render_pro_subtitles(
                                s_text, s_dur, target_size, 
                                full_highlight=is_movie_mode,
                                is_dynamic=False,  # Forced to False to remove yellow highlights
                                word_timings=relevant_timings,
                                y_position=y_pos,
                                is_highlight=is_highlight
                            )
                            
                            if d_txt_clip:
                                d_txt_clip = d_txt_clip.with_start(s_start)
                                
                                # v26.0: Metadata already added to all_srt_items above
                                pass
                                
                                # v17.3.3: Prevención de Solapamiento (Clipping)
                                # Si hay un subtítulo siguiente en la misma posición vertical, 
                                # recortamos este clip para que termine justo cuando empieza el otro.
                                try:
                                    if idx + 1 < len(scene.subtitles):
                                        next_sub = scene.subtitles[idx + 1]
                                        # Solo si están en la misma línea (evita interferir entre SUB y PHO:h)
                                        if next_sub.get('y_position', 0.70) == y_pos:
                                            # Calculamos el inicio del siguiente para recortar
                                            # (asumimos la misma lógica de timing del bucle)
                                            if is_dynamic and hasattr(scene, 'word_timings') and scene.word_timings:
                                                next_offset = next_sub.get('offset', 0)
                                                if next_offset < len(scene.word_timings):
                                                    next_start = scene.word_timings[next_offset]['start']
                                                    if next_sub.get('is_highlight', False):
                                                        next_start = max(0, next_start - 0.20)
                                                    
                                                    # Recortar duración si hay solapamiento
                                                    if s_start + s_dur > next_start:
                                                        s_dur = max(0.1, next_start - s_start)
                                                        d_txt_clip = d_txt_clip.with_duration(s_dur)
                                                        logger.log(f"      [Clip] Solapamiento detectado. Recortando chunk {idx} a {s_dur:.2f}s")
                                except: pass

                                sub_clips_dynamic.append(d_txt_clip)
                        
                        if sub_clips_dynamic:
                            # v26.0: Bypass MoviePy text rendering for stability/speed (handled by FFmpeg injection)
                            # clip = CompositeVideoClip([clip] + sub_clips_dynamic)
                            pass
                            logger.log(f"    [OK] Desplegados {len(sub_clips_dynamic)} subtitulos PRO v16.5.")
                except Exception as e:
                    import traceback
                    logger.log(f"    [WARNING] Error renderizando subtitulos PRO: {e}\n{traceback.format_exc()}")

                # v14.0 Audio Mixing: Mix Voice + Original Video Sound (if volume > 0)
                # v14.3: Robust check for audio presence
                if audio_clip and clip.audio:
                    from moviepy import CompositeAudioClip
                    mixed_audio = CompositeAudioClip([audio_clip, clip.audio])
                    clip = clip.with_audio(mixed_audio)
                elif audio_clip:
                    clip = clip.with_audio(audio_clip)
                elif clip.audio:
                    # v14.3: If NO text/voice, but video has audio, leave it as is
                    logger.log(f"    🔊 [Audio] Usando audio original del video (No hay locución).")
                else:
                    # v14.3: No voice, no video audio = silent clip
                    #logger.log(f"    🔇 [Audio] Escena silenciosa (No hay voz ni audio de video).")
                    clip = clip.without_audio()

                block_scene_clips.append(clip)
                
                # Timestamps
                m, s = divmod(int(current_time), 60)
                timestamps_list.append(f"{m:02d}:{s:02d} {scene.title}")
                
                # Ducking Intervals
                # v14.3 Smart Ducking: Only registr intervals if there is real text/voice
                if audio_clip:
                    if hasattr(scene, 'voice_intervals') and scene.voice_intervals:
                        for vs, ve in scene.voice_intervals: block_voice_intervals.append((block_cursor + vs, block_cursor + ve))
                    else: 
                        block_voice_intervals.append((block_cursor, block_cursor + voice_duration))
                
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
                            
                            # Safe Block Composition (v15.7 Fix)
                            b_sources = []
                            if block_video.audio: b_sources.append(block_video.audio)
                            if bg_audio_final: b_sources.append(bg_audio_final)
                            
                            if b_sources:
                                final_audio = CompositeAudioClip(b_sources)
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
                # v26.0: Advance global cursor for next block
                video_base_cursor += block_video.duration

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
                
                # Initialize bg_audio safety
                bg_audio = None

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
                            if t.size == 0: return np.zeros((0, 1))
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
                    
                    # Safe Audio Composition (v15.7 Fix for IndexError)
                    audio_sources = []
                    if final_video.audio: audio_sources.append(final_video.audio)
                    if bg_audio_final: audio_sources.append(bg_audio_final)
                    
                    if audio_sources:
                        final_video = final_video.with_audio(CompositeAudioClip(audio_sources))
                    
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

            # v13.0: Custom Cache Logger (Terminology Sync)
            cache_logger = CacheProgressBarLogger(project.id)

            final_video.write_videofile(
                output_path, 
                ffmpeg_params=["-pix_fmt", "yuv420p"], 
                logger=cache_logger, # v13.0: Real-time Item visibility
                **render_params
            )
            
            project.output_video.name = f"videos/{output_filename}"
            project.duration = float(final_video.duration)
            project.timestamps = "\n".join(timestamps_list)
            # v26.6: Deferred completion until after subtitle injection (Wait for ASS burn-in)
            project.progress_total = 95.0
            project.save(update_fields=['output_video', 'duration', 'timestamps', 'progress_total'])
            
            logger.log(f"✅ ¡Video base generado! ({output_path})")
            phase1_end = time.time()
            logger.log(f"⏱️ FASE 1 (Video Base) Duración: {phase1_end - start_time:.2f}s")

            # ═══════════════════════════════════════════════════════════════════
            # v26.0 POST-INJECTION PHASE (THE YOUTUBE WAY)
            # ═══════════════════════════════════════════════════════════════════
            if all_srt_items:
                logger.log("🎬 Iniciando Inyección Final de Subtítulos v26.1 (Format: ASS)...")
                # v26.1: Use .ass instead of .srt for professional styling and position control
                ass_path = output_path.replace('.mp4', '.ass')
                final_output_path = output_path.replace('.mp4', '_final.mp4')
                
                # 1. Compile ASS (Professionally styled)
                from .subtitle_utils import compile_full_script_ass
                if compile_full_script_ass(all_srt_items, ass_path):
                    # 2. FFmpeg Injection Command (Automated Binary Discovery)
                    import subprocess
                    import imageio_ffmpeg
                    ff_exe = imageio_ffmpeg.get_ffmpeg_exe()
                    
                    # v26.4: HYBRID PATH STRATEGY (The Golden Mean)
                    # We run FFmpeg anchored to BASE_DIR to ensure the relative ASS path (no colons!) works.
                    # HOWEVER, we use ABSOLUTE paths for Input/Output to guarantee file discovery regardless of CWD.
                    try:
                        base_dir = str(settings.BASE_DIR)
                        rel_ass_path = os.path.relpath(ass_path, base_dir).replace('\\', '/')
                        # Input/Output remain Absolute for maximum reliability
                        
                        # v27.1: Re-apply GPU Acceleration for Subtitle Injection (The "P1" Fix)
                        video_codec_params = ['-c:v', 'libx264', '-preset', 'ultrafast'] # CPU Default

                        if project.render_mode == 'gpu':
                             # NVENC P1 = Fastest possible encoding (Low Latency / High Perf)
                             logger.log("  🚀 [GPU] Activando NVENC P1 para inyección de subtítulos.")
                             video_codec_params = ['-c:v', 'h264_nvenc', '-preset', 'p1', '-b:v', '5M']

                        ff_cmd = [
                            ff_exe, '-y', '-i', output_path,
                            '-vf', f"ass=filename='{rel_ass_path}'",
                            *video_codec_params,
                            '-c:a', 'copy',
                            final_output_path
                        ]
                        
                        logger.log(f"🎬 Ejecutando FFmpeg (CWD: {base_dir}): {ff_cmd}")
                        
                        # V26.5: Robust Execution with Timeout & Stderr Capture
                        try:
                            # 120s timeout to prevent zombie processes
                            result = subprocess.run(ff_cmd, check=True, capture_output=True, cwd=base_dir, timeout=120)
                            
                            # Reemplazo final Robusto (Anti-Lock)
                            if os.path.exists(final_output_path):
                                try:
                                    if os.path.exists(output_path):
                                        try: os.remove(output_path)
                                        except OSError: pass # Try to rename anyway
                                    
                                    os.rename(final_output_path, output_path)
                                    logger.log(f"✅ Fusión exitosa. Video final reemplazó al original: {output_path}")
                                except OSError as lock_err:
                                    logger.log(f"⚠️ LOCK DETECTADO: No se pudo sobrescribir {output_path}. Usando ruta alternativa.")
                                    # CRITICAL: Return the new file to avoid serving the old one
                                    output_path = final_output_path
                                    # Update project model to point to the new file
                                    # We use RELATIVE path for Django FileField
                                    rel_new_path = f"videos/{os.path.basename(output_path)}"
                                    project.output_video.name = rel_new_path
                                    project.save(update_fields=['output_video'])
                                    logger.log(f"⚠️ Proyecto actualizado a: {rel_new_path}")

                            else:
                                logger.log("⚠️ Error: El video finalizado no se generó (File missing).")

                        except subprocess.CalledProcessError as e:
                            logger.log(f"❌ Error FFmpeg (Exit {e.returncode}): {e.stderr.decode('utf-8', errors='replace')}")
                            # Don't raise immediately, let the original video survive if burning fails?
                            # No, burning is critical.
                            raise e
                        except subprocess.TimeoutExpired:
                            logger.log("❌ Error: Tiempo de espera agotado en FFmpeg (120s).")
                            raise

                    except Exception as fe:
                        logger.log(f"⚠️ Error en fusión FFmpeg: {fe}")
                        # If burning fails, we still have the original video (output_path).
                        # We proceed, but warn.

        project.progress_total = 100.0 # Ensure final progress is 100%
        # v26.5: output_path might have changed!
        # Ensure the final project status reflects the correct file if changed earlier
        project.status = 'completed'; project.save(update_fields=['status', 'progress_total'])
        
        # v27.0: AUTOMATED GARBAGE COLLECTION
        try:
            from .utils import cleanup_garbage
            cleanup_garbage(settings.BASE_DIR)
        except Exception as ge:
            logger.log(f"⚠️ Error en Garbage Collector: {ge}")

        play_finish_sound(success=True)
        phase2_end = time.time()
        logger.log(f"⏱️ FASE 2 (Subtítulos) Duración: {phase2_end - phase1_end:.2f}s")
        logger.log(f"[Done] Exito en {phase2_end-start_time:.1f} segundos!")

    except Exception as e:
        logger.log(f"[FATAL] Error en renderizado: {e}")
        project.status = 'failed'; project.save(update_fields=['status'])
        play_finish_sound(success=False)
        raise e
    finally:
        # v12.5.3: Clear active project from global cache
        from django.core.cache import cache
        cache.delete("active_rendering_project_id")
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
