"""
AVGL v5.6.9 - Shielded Multilayer Engine (Absolute Overlay Mapping)
Fixes the missing overlay in Scene 3.1 by supporting object attributes and dict keys.
"""

import os
import time
import re
import numpy as np
import asyncio
from django.conf import settings

def safe_float(val, default=0.0):
    try:
        if val is None or str(val).strip() == "": return default
        return float(val)
    except:
        return default

# ═══════════════════════════════════════════════════════════════════
# 1. Kinematic Core
# ═══════════════════════════════════════════════════════════════════

def apply_ken_burns(image_path, duration, target_size, zoom="1.0:1.3", move="HOR:50:50", human_signature=False, human_amplitude=1.0):
    from moviepy import ImageClip; from PIL import Image
    z_parts = zoom.split(':') if (zoom and ':' in zoom) else ['1.0', '1.0']
    zs, ze = float(z_parts[0]), float(z_parts[1])
    m_parts = move.split(':') if move else ['HOR', '50', '50']
    md, ms, me = m_parts[0].upper(), float(m_parts[1]), float(m_parts[2])
    
    img = Image.open(image_path).convert('RGB')
    tw, th = target_size
    sw, sh = tw / img.size[0], th / img.size[1]
    bs = max(sw, sh)
    
    pan_b = 1.25 
    max_z = max(zs, ze)
    total_scale = bs * max_z * pan_b
    
    wi = img.resize((int(img.size[0]*total_scale), int(img.size[1]*total_scale)), Image.Resampling.BICUBIC)
    inp = np.array(wi)

    def crop_frame(gf, t):
        prog = t / duration if duration > 0 else 0
        cz = zs + (ze - zs) * prog
        cw, ch = int(tw * (max_z / cz)), int(th * (max_z / cz))
        
        cx, cy = 50.0, 50.0; val = ms + (me - ms) * prog
        if md == 'HOR': cx = val
        elif md == 'VER': cy = val
        if human_signature:
            cx += (np.sin(t*7.0)*0.2) * human_amplitude
            cy += (np.cos(t*8.0)*0.2) * human_amplitude
            
        pxcx, pxcy = int(wi.size[0]*(cx/100.0)), int(wi.size[1]*(cy/100.0))
        x1 = max(0, min(wi.size[0]-cw, pxcx - cw//2))
        y1 = max(0, min(wi.size[1]-ch, pxcy - ch//2))
        return np.array(Image.fromarray(inp[y1:y1+ch, x1:x1+cw]).resize((tw, th), Image.Resampling.LANCZOS))

    return ImageClip(np.zeros((th, tw, 3), dtype='uint8'), duration=duration).transform(crop_frame)

# ═══════════════════════════════════════════════════════════════════
# 2. Subtitle Engine
# ═══════════════════════════════════════════════════════════════════

def format_ass_time(seconds):
    td = float(seconds)
    hours, rem = divmod(td, 3600); minutes, rem = divmod(rem, 60); secs = int(rem); csecs = int(round((rem - secs) * 100))
    if csecs == 100: secs += 1; csecs = 0
    return f"{int(hours)}:{int(minutes):02d}:{secs:02d}.{csecs:02d}"

def generate_ass_karaoke(word_timings, output_path, target_size=(1080, 1920), subs_y=0.7, static_subs=None):
    margin_v_main = int(target_size[1] * (1.0 - subs_y))
    header = [f"[Script Info]\nScriptType: v4.00+\nPlayResX: {target_size[0]}\nPlayResY: {target_size[1]}\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"]
    header.append(f"Style: AlphaMain,Arial,80,&H00FFFFFF,&H0000FFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,4,1.5,2,80,80,{margin_v_main},1\n")
    header.append(f"Style: AlphaTitle,Arial,90,&H0000FFFF,&H00000000,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,5,0,8,100,100,200,1\n")
    header.append(f"Style: AlphaHeader,Arial,80,&H00008CFF,&H00000000,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,3.5,1,2,80,80,{margin_v_main},1\n")
    header.append("\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    lines = ["".join(header)]
    if static_subs:
        for sub in static_subs:
            style = "AlphaHeader" if sub.get('style') == 'Header' else ("AlphaTitle" if sub.get('y_pos', 0.15) < 0.5 else "AlphaMain")
            mv = int(sub['y_pos'] * target_size[1]) if style == "AlphaTitle" else int((1.0 - sub['y_pos']) * target_size[1])
            lines.append(f"Dialogue: 1,{format_ass_time(sub['start'])},{format_ass_time(sub['end'])},{style},,0,0,{mv},,{sub['text']}\n")
    curr_line = []
    for wt in word_timings:
        if len(curr_line) >= 10 or (curr_line and (wt['start'] - curr_line[-1]['end']) > 0.8):
             if curr_line:
                content = "".join([f"{{\\k{int((w['end'] - w['start']) * 100)}}}{w['word']} " for w in curr_line])
                lines.append(f"Dialogue: 0,{format_ass_time(curr_line[0]['start'])},{format_ass_time(curr_line[-1]['end'] + 0.3)},AlphaMain,,0,0,{margin_v_main},,{content.strip()}\n")
                curr_line = []
        curr_line.append(wt)
    if curr_line: lines.append(f"Dialogue: 0,{format_ass_time(curr_line[0]['start'])},{format_ass_time(curr_line[-1]['end'] + 0.5)},AlphaMain,,0,0,{margin_v_main},,{' '.join([w['word'] for w in curr_line])}\n")
    with open(output_path, 'w', encoding='utf-8') as f: f.write("".join(lines))
    return True

# ═══════════════════════════════════════════════════════════════════
# 3. Asset Resolution
# ═══════════════════════════════════════════════════════════════════

def resolve_asset_path_robust(asset_raw_id, assets_dir):
    if not asset_raw_id: return None
    raw_str = str(asset_raw_id)
    if raw_str.lower() == "smoke": 
        pot = resolve_asset_path_robust("viento_polvo_de_estepa", assets_dir); 
        if pot: return pot
        return resolve_asset_path_robust("dust", assets_dir)
    clean_id = raw_str.replace("/media/assets/", "").replace("\\", "/").strip().strip("/")
    basename = os.path.basename(clean_id)
    variants = [basename, basename.replace(" ", "_"), basename.replace("_", " "), basename.lower(), basename.lower().replace(" ", "_")]
    for var in variants:
        pot = os.path.normpath(os.path.join(assets_dir, var))
        if os.path.exists(pot) and os.path.isfile(pot): return pot
        for ext in ['.mp4', '.mov', '.png', '.jpg', '.jpeg', '.PNG', '.JPG']:
            if os.path.exists(pot + ext) and os.path.isfile(pot + ext): return pot + ext
    try:
        for r, ds, fs in os.walk(assets_dir):
            for f in fs:
                f_name = f.lower()
                for var in variants:
                    v_low = var.lower()
                    if f_name == v_low or f_name.split('.')[0] == v_low:
                         return os.path.normpath(os.path.join(r, f))
    except: pass
    return None

def process_video_asset(path, duration, target_size, fit=None):
    from moviepy import VideoFileClip, vfx
    vc = VideoFileClip(path).without_audio()
    if vc.duration < duration: vc = vc.with_effects([vfx.Loop(duration=duration)])
    vc = vc.subclipped(0, duration)
    tw, th = target_size
    bs = min(tw/vc.size[0], th/vc.size[1]) if (fit == "contain" or fit is True) else max(tw/vc.size[0], th/vc.size[1])
    return vc.resized(bs).with_position("center").with_duration(duration)

# ═══════════════════════════════════════════════════════════════════
# 4. Engine Core
# ═══════════════════════════════════════════════════════════════════

def generate_video_avgl(project):
    from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, VideoFileClip, CompositeAudioClip, CompositeVideoClip, afx, vfx
    from .avgl_engine import parse_avgl_json, translate_emotions, wrap_ssml, generate_audio_elevenlabs; from .utils import ProjectLogger
    import asyncio, numpy as np, edge_tts
    
    start_time_total = time.time(); project.status = 'processing'; project.save(); logger = ProjectLogger(project)
    try:
        script = parse_avgl_json(project.script_text)
    except Exception as e:
        logger.log(f"❌ JSON Error: {e}"); project.status = 'error'; project.save(); return
    
    duck_att = safe_float(script.settings.get('audio_ducking_attack', 0.15))
    duck_rel = safe_float(script.settings.get('audio_ducking_release', 0.35))
    logger.log(f"🚀 AVGL v5.6.9 - Shielded Engine (Absolute Mapping)")

    assets_dir = os.path.join(settings.MEDIA_ROOT, 'assets')
    overlays_dir = os.path.join(settings.MEDIA_ROOT, 'overlays')
    target_size = (1080, 1920) if project.aspect_ratio == 'portrait' else (1920, 1080)
    
    if project.voice_id:
        ov = script.voice; script.voice = project.voice_id
        for b in script.blocks:
            if not b.voice or b.voice == ov: b.voice = project.voice_id
            for s in b.scenes:
                if not s.voice or s.voice == ov: s.voice = project.voice_id

    # 1. AUDIO GEN
    all_scenes = script.get_all_scenes(); scene_audio_map = {}
    for i, scene in enumerate(all_scenes):
        ap = os.path.join(settings.MEDIA_ROOT, 'temp_audio', f"p{project.id}_s{i}.mp3"); os.makedirs(os.path.dirname(ap), exist_ok=True)
        if not scene.text: scene_audio_map[scene] = None; continue
        txt = re.sub(r'\(.*?\)', '', re.sub(r'^\[[^\]]+\]\s*', '', scene.text)).strip()
        try:
            if project.engine == 'edge':
                rate = f"+{int((scene.speed-1)*100)}%" if scene.speed != 1.0 else os.getenv("EDGE_TTS_RATE", "+0%")
                ssml = wrap_ssml(translate_emotions(txt, use_ssml=False), scene.voice, rate, pitch=scene.pitch)
                async def tts_task():
                    comm = edge_tts.Communicate(ssml, scene.voice, rate=rate); tms = []
                    with open(ap, "wb") as f:
                        async for ev in comm.stream():
                            if ev.get("type") == "audio": f.write(ev.get("data"))
                            elif ev.get("type") == "WordBoundary": tms.append({"start": ev['offset']/1e7, "end": (ev['offset']+ev['duration'])/1e7, "word": ev['text']})
                    return tms
                loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop); scene.word_timings = loop.run_until_complete(tts_task()); scene_audio_map[scene] = ap; loop.close()
            else:
                loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
                if loop.run_until_complete(generate_audio_elevenlabs(translate_emotions(txt, use_ssml=True), ap, os.getenv('ELEVENLABS_VOICE_ID'), os.getenv('ELEVENLABS_API_KEY'))): scene_audio_map[scene] = ap
                else: scene_audio_map[scene] = None
                loop.close()
        except: scene_audio_map[scene] = None

    # 2. RENDER PROCESS
    render_start = time.time()
    video_blocks = []; audio_layers = []; cur_t = 0.0; all_word_timings = []; all_static_subs = []; mute_intervals = []; all_voice_intervals = []
    for b in script.blocks:
        project.refresh_from_db(); 
        if project.status == 'cancelled': return
        logger.log(f"📦 Bloque: {b.title}")
        sc_clips = []; b_start = cur_t; b_voice_intervals = []
        for s in b.scenes:
            ac_path = scene_audio_map.get(s); ac = AudioFileClip(ac_path) if ac_path and os.path.exists(ac_path) else None
            vdur = ac.duration if ac else 0.0
            if ac: 
                audio_layers.append(ac.with_start(cur_t)); b_voice_intervals.append((cur_t, cur_t+vdur)); all_voice_intervals.append((cur_t, cur_t+vdur))
            dur = vdur + s.pause if vdur > 0 else 1.0
            
            layers = []
            bg_dat = getattr(s, 'layers', {}).get('background') if hasattr(s, 'layers') else (s.assets[0] if s.assets else None)
            
            # Smart Overlay Discovery (Object vs Dict compatible)
            over_raw = getattr(s, 'layers', {}).get('overlay') if hasattr(s, 'layers') else None
            
            # If no root overlay, look into background object
            if not over_raw and bg_dat:
                if isinstance(bg_dat, dict): over_raw = {'id': bg_dat.get('overlay'), 'opacity': 0.45} if bg_dat.get('overlay') else None
                else: over_raw = {'id': getattr(bg_dat, 'overlay', None), 'opacity': 0.45} if getattr(bg_dat, 'overlay', None) else None
            
            if bg_dat:
                bg_id = bg_dat.get('id') if isinstance(bg_dat, dict) else bg_dat.type
                ap_p = resolve_asset_path_robust(bg_id, assets_dir)
                if ap_p:
                    if ap_p.lower().endswith(('.mp4', '.mov')): layers.append(process_video_asset(ap_p, dur, target_size, fit=bg_dat.get('fit') if isinstance(bg_dat, dict) else bg_dat.fit))
                    else: layers.append(apply_ken_burns(ap_p, dur, target_size, zoom=bg_dat.get('zoom') if isinstance(bg_dat, dict) else (bg_dat.zoom or "1.0:1.3"), move=bg_dat.get('move') if isinstance(bg_dat, dict) else (bg_dat.move or "HOR:50:50"), human_signature=getattr(bg_dat, 'human_signature', project.human_signature), human_amplitude=getattr(bg_dat, 'human_amplitude', project.human_amplitude)))
            if not layers: layers.append(ImageClip(np.zeros((target_size[1], target_size[0], 3), dtype=np.uint8), duration=dur))

            main_dat = getattr(s, 'layers', {}).get('main') if hasattr(s, 'layers') else None
            if main_dat:
                mp_p = resolve_asset_path_robust(main_dat.get('id') if isinstance(main_dat, dict) else main_dat.type, assets_dir)
                if mp_p:
                    mh = int(target_size[1]*0.8); mo = safe_float(main_dat.get('opacity') if isinstance(main_dat, dict) else main_dat.opacity, 1.0)
                    if mp_p.lower().endswith(('.mp4', '.mov')): layers.append(VideoFileClip(mp_p, has_mask=True).resized(height=mh).with_opacity(mo).subclipped(0, min(100, dur)))
                    else: layers.append(ImageClip(mp_p).resized(height=mh).with_opacity(mo).with_duration(dur).with_position('center'))

            if over_raw:
                over_id = over_raw.get('id') if isinstance(over_raw, dict) else (getattr(over_raw, 'type', None) or getattr(over_raw, 'id', None))
                if over_id:
                    op_p = resolve_asset_path_robust(over_id, overlays_dir) or resolve_asset_path_robust(over_id, assets_dir)
                    if op_p:
                        # VIGNETTE SPECIAL HANDLING: Opaque by default if name matches
                        is_vignette = "vignette" in over_id.lower()
                        oo = 1.0 if is_vignette else safe_float(over_raw.get('opacity') if isinstance(over_raw, dict) else getattr(over_raw, 'opacity', 0.45), 0.45)
                        
                        if op_p.lower().endswith(('.mp4', '.mov')): 
                            oc = VideoFileClip(op_p).resized(target_size).with_effects([vfx.Loop(duration=dur)]).subclipped(0, dur)
                            oc = oc.with_mask(oc.to_mask()).with_opacity(oo).without_audio()
                            layers.append(oc)
                        else: layers.append(ImageClip(op_p).resized(target_size).with_opacity(oo).with_duration(dur).with_position('center'))
                    else: logger.log(f"  ⚠️ Overlay no encontrado: {over_id}")

            sc_clips.append(CompositeVideoClip(layers, size=target_size, bg_color=(0,0,0)).without_audio()); cur_t += dur
            if s.word_timings:
                disp = getattr(s, 'display_text', s.text).split()
                for i1, wt in enumerate(s.word_timings): all_word_timings.append({"start": cur_t-dur+wt['start'], "end": cur_t-dur+wt['end'], "word": disp[i1] if i1 < len(disp) else wt['word']})
            if s.subtitles:
                for sub in s.subtitles: all_static_subs.append({"text": sub['text'], "start": cur_t-dur+(sub['offset']*(dur/len(s.text.split())) if s.text.split() else 0), "end": cur_t-dur+(sub['offset']*(dur/len(s.text.split())) if s.text.split() else 0)+((sub['phonetic_count']*0.075) if sub.get('phonetic_count') else dur), "y_pos": sub.get('y_position', 0.15)})
        if b.music:
            from .models import Music
            mo = Music.objects.filter(file__icontains=os.path.basename(b.music)).first()
            if mo and os.path.exists(mo.file.path):
                bd = cur_t - b_start; bga = AudioFileClip(mo.file.path).with_effects([afx.AudioLoop(n_loops=int(bd/120)+1)]).with_duration(bd).with_effects([afx.AudioFadeOut(0.5)])
                bvk, dr = safe_float(b.volume, 0.2), safe_float(script.settings.get('audio_ducking_ratio', 0.17))
                def b_vol(gf, t, b_s=b_start, b_v=b_voice_intervals, b_pk=bvk, d_r=dr, att=duck_att, rel=duck_rel):
                    at = t if isinstance(t, np.ndarray) else np.array([t]); res = np.full(at.shape, b_pk)
                    for vs, ve in b_v:
                        v_s, v_e = vs - b_s, ve - b_s; res[(at >= v_s) & (at <= v_e)] = b_pk * d_r
                        m_att = (at >= v_s - att) & (at < v_s); res[m_att] = b_pk - (b_pk * (1 - d_r) * (at[m_att] - (v_s - att)) / att)
                        m_rel = (at > v_e) & (at <= v_e + rel); res[m_rel] = (b_pk * d_r) + (b_pk * (1 - d_r) * (at[m_rel] - v_e) / rel)
                    return gf(t) * (res.reshape(-1, 1) if isinstance(t, np.ndarray) else res[0])
                audio_layers.append(bga.transform(b_vol).with_start(b_start)); mute_intervals.append((b_start, cur_t))
        video_blocks.append(concatenate_videoclips(sc_clips, method="chain"))

    final_v = concatenate_videoclips(video_blocks, method="chain")
    try:
        gm_n = os.path.basename(project.background_music.file.name) if project.background_music else script.background_music
        if gm_n:
            from .models import Music
            gm = Music.objects.filter(file__icontains=gm_n).first()
            if gm and os.path.exists(gm.file.path):
                bga = AudioFileClip(gm.file.path).with_effects([afx.AudioLoop(n_loops=int(final_v.duration/120)+1)]).with_duration(final_v.duration)
                gv, dr = safe_float(script.music_volume or project.music_volume, 0.2), safe_float(script.settings.get('audio_ducking_ratio', 0.17))
                def g_vol(gf, t, g_v=gv, d_r=dr, m_i=mute_intervals, v_i=all_voice_intervals, att=duck_att, rel=duck_rel):
                    at = t if isinstance(t, np.ndarray) else np.array([t]); res = np.full(at.shape, g_v); cross = 0.5
                    for s, e in m_i: res[(at >= s) & (at <= e)] = 0; m_in = (at>=s-cross) & (at<s); res[m_in] *= (1.0-(at[m_in]-(s-cross))/cross); m_out = (at>e) & (at<=e+cross); res[m_out] *= (at[m_out]-e)/cross
                    for s, e in v_i: res[(at>=s)&(at<=e)] *= d_r; m_att = (at>=s-att)&(at<s); res[m_att] = res[m_att]*(1.0-(1.0-d_r)*(at[m_att]-(s-att))/att); m_rel = (at>e)&(at<=e+rel); res[m_rel] = (res[m_rel]*d_r)+(res[m_rel]*(1.0-d_r)*(at[m_rel]-e)/rel)
                    return gf(t) * (res.reshape(-1, 1) if isinstance(t, np.ndarray) else res[0])
                audio_layers.append(bga.transform(g_vol).with_start(0))
        final_v = final_v.with_audio(CompositeAudioClip(audio_layers))
    except Exception as me:
        logger.log(f"⚠️ SHIELD Mix: {me}")
    
    op = os.path.join(settings.MEDIA_ROOT, 'videos', f"project_{project.id}.mp4"); rp = op.replace(".mp4", "_raw.mp4")
    final_v.write_videofile(rp, fps=30, codec='libx264', audio_codec='aac', preset='ultrafast', threads=8)
    render_dur = time.time() - render_start

    # 3. SUBTITLE SHIELD & TIMER
    sub_start = time.time(); sub_dur = 0.0
    try:
        if all_word_timings or all_static_subs:
            asp = op.replace(".mp4", ".ass"); show_d = script.settings.get('dynamic_subtitles', False)
            generate_ass_karaoke(all_word_timings if show_d else [], asp, target_size, safe_float(script.settings.get('subtitles_y_position', 0.7)), all_static_subs)
            rel_asp = os.path.relpath(asp, os.getcwd()).replace('\\', '/')
            import subprocess; subprocess.run(['ffmpeg', '-y', '-i', rp, '-vf', f"subtitles='{rel_asp}'", '-c:a', 'copy', op], check=True)
            os.remove(rp); os.remove(asp); sub_dur = time.time() - sub_start
        else: os.replace(rp, op)
    except Exception as se:
        logger.log(f"⚠️ SHIELD Subs Fix Error: {se}")
        if os.path.exists(rp): os.replace(rp, op)
    
    total_dur = time.time() - start_time_total
    project.output_video.name = f"videos/project_{project.id}.mp4"; project.status = 'completed'; project.save()
    logger.log(f"⏱️ Telemetría: Render [{render_dur:.1f}s] | Subs [{sub_dur:.1f}s] | TOTAL [{total_dur:.1f}s]")
    logger.log(f"✨ ¡Generación v5.6.9 exitosa!"); return op
