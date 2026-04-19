import os
import asyncio
import random
import json
import re
import time
from django.conf import settings
from moviepy import AudioFileClip, concatenate_audioclips, AudioClip
import numpy as np

def safe_float(val, default=0.0):
    try:
        if val is None or str(val).strip() == "": return default
        # v36.0: Support for human time format (min:seg or min:seg.ms)
        s = str(val).strip().replace(',', '.')
        if ':' in s:
            parts = s.split(':')
            if len(parts) == 2:
                # 02:30 -> 150.0
                return float(parts[0]) * 60 + float(parts[1])
            elif len(parts) == 3:
                # 01:02:30 -> 3750.0
                return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
        return float(s)
    except:
        return default

# ═══════════════════════════════════════════════════════════════════
# AVGL v4.0 - Global Voice Configurations
# ═══════════════════════════════════════════════════════════════════

VOICES_CONFIG = {
    'ETHAN': 'es-MX-JorgeNeural',
    'CHARLI': 'es-DO-EmilioNeural',
    'CARLOS': 'es-DO-EmilioNeural',
    'SONY': 'es-MX-DaliaNeural',
    'NARRADOR': 'es-MX-JorgeNeural',
    'CIENTIFICO': 'es-MX-JorgeNeural',
    'JOVEN': 'es-DO-EmilioNeural'
}

ACTIONS_CONFIG = {
    '[TOS]': 'cof, cof...',
    '[AJEM]': 'ajem...',
    '[SUSPIRO]': 'uf...',
    '[SORPRESA]': '¡oh!',
    '[RISA]': 'ja, ja, ja...'
}

class AVGLAsset:
    def __init__(self, asset_type, zoom=None, move=None, overlay=None, fit=False, shake=False, rotate=None, shake_intensity=5, w_rotate=None, video_volume=None, fast_assembly=False, cinema_mode=False, start_time=0.0, end_time=None, human_signature=None, human_amplitude=1.0):
        self.type = asset_type
        self.zoom = zoom
        self.move = move
        self.overlay = overlay
        self.fit = fit
        self.shake = shake
        self.rotate = rotate
        self.shake_intensity = shake_intensity
        self.w_rotate = w_rotate
        self.video_volume = video_volume
        self.fast_assembly = fast_assembly
        self.cinema_mode = cinema_mode
        self.start_time = start_time
        self.end_time = end_time
        self.human_signature = human_signature
        self.human_amplitude = safe_float(human_amplitude, 1.0)

class AVGLSFX:
    def __init__(self, sfx_type, volume=0.5, offset=0):
        self.type = sfx_type
        self.volume = volume
        self.offset = offset

class AVGLScene:
    def __init__(self, title):
        self.title = title
        self.text = ""
        self.voice = None
        self.audio = None
        self.speed = None
        self.pitch = None
        self.assets = []
        self.sfx = []
        self.pause = 0.0
        self.subtitle = ""
        self.subtitles = []
        self.voice_intervals = [] # v6.5: Granular Ducking Intervals (start, end)
        self.word_timings = []    # v16.5: Word-level timestamps for Dynamic Subtitles
        self.group_id = None
        self.group_settings = None
        # v20.4: Manual Override Support
        self.duration = 0.0
        self.force_duration = False
        self.lipsync = False # v9.0: Local Lip-Sync support
        self.language = None # v5.1: Per-scene language
        self.dubbing_mode = None # v5.1: Per-scene dubbing mode
        self.silent = False # v28.0: Mute mode (Subtitles without TTS)

class AVGLBlock:
    def __init__(self, title, music=None, volume=0.2):
        self.title = title
        self.scenes = []
        self.music = music
        self.volume = volume

class AVGLScript:
    def __init__(self, title):
        self.title = title
        self.blocks = []
        self.voice = "es-DO-EmilioNeural"
        self.speed = 1.0
        self.style = "neutral"
        self.background_music = None
        self.music_volume = 0.18
        # v7.5: Global Metadata for YouTube/SEO
        self.fuentes = ""
        self.tags = ""
        self.hashtags = ""
        self.music_volume_lock = False
        self.thumbnail = None
        self.settings = {}

    def get_all_scenes(self):
        scenes = []
        for block in self.blocks:
            scenes.extend(block.scenes)
        return scenes

# ═══════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════

def parse_speed(val):
    if val is None: return 1.0
    if isinstance(val, (int, float)): return float(val)
    s = str(val).strip()
    if s.endswith('%'):
        try:
            pct = int(s.replace('%', ''))
            return 1.0 + (pct / 100.0)
        except: return 1.0
    return 1.0

def parse_escena(text):
    """
    v17.2: Parses scene text and extracts 3 separate strings:
    - fonetica: Text for TTS (uses phonetic parts from PHO tags)
    - display: Text for subtitles (uses display parts from PHO tags)
    - highlights: List of dicts with highlighted text and word offset
    
    Example:
        Input: "Esto es [PHO:h]cul|cool[/PHO] ;)"
        Output: ("Esto es cul ;)", "Esto es cool ;)", [{"text": "cool", "offset":2}])
    
    v17.2.5: Highlights now include word offset for correct timing sync
    """
    import re
    
    fonetica_parts = []
    display_parts = []
    highlights = []
    
    # Pattern to match [PHO] or [PHO:modifier] tags (any modifier: h, s, e, t, etc.)
    # v17.2.3: Fixed to support all modifiers, not just :h
    pho_pattern = r'\[PHO(?::[a-zA-Z]+)?\](.*?)\[/PHO\]'
    
    last_idx = 0
    for match in re.finditer(pho_pattern, text, re.IGNORECASE):
        # Add literal text before tag
        before = text[last_idx:match.start()]
        fonetica_parts.append(before)
        display_parts.append(before)
        
        # Extract tag content
        content = match.group(1)
        is_highlight = ':h' in match.group(0).lower()
        
        # Split by | to get phonetic and display
        if '|' in content:
            parts = content.split('|', 1)
            phonetic = parts[0].strip()
            display_text = parts[1].strip()
        else:
            phonetic = content.strip()
            display_text = "" # v19.6.2: No pipe = No DYN (Architect's Golden Rule)
        
        # Calculate word offset BEFORE adding phonetic to parts
        # v17.2.5: Offset is where phonetic starts in fonetica_str
        current_fonetica = ''.join(fonetica_parts)
        word_offset = len(current_fonetica.split())
        
        # Add to respective strings
        fonetica_parts.append(phonetic)
        display_parts.append(display_text)
        
        # If highlight, add to list with offset
        if is_highlight:
            # v19.6.3: Use phonetic text if display is empty (asymmetric mode)
            h_text = display_text if display_text else phonetic
            highlights.append({
                "text": h_text,
                "offset": word_offset
            })
        
        last_idx = match.end()
    
    # Add remaining text
    rest = text[last_idx:]
    fonetica_parts.append(rest)
    display_parts.append(rest)
    
    fonetica_str = ''.join(fonetica_parts)
    display_str = ''.join(display_parts)
    
    return fonetica_str, display_str, highlights

def extract_subtitles_v35(text, force_dynamic=False):
    """
    Extracts subtitles and narration from tags.
    v17.2.7: REFACTOR - Split original text first, then parse chunks.
    Ensures perfect sync between fonetica_str and display_str.
    """
    import re
    
    # v17.2.19: Hardened cleanup with DOTALL support
    def _cleanup(content):
        if not content: return ""
        # Remove all bracket tags like [TENSO], [EPICO], [DYN], etc.
        res = re.sub(r'\[.*?\]', '', content, flags=re.IGNORECASE | re.DOTALL)
        # v27.3: SE PERMITEN PARÉNTESIS (Arquitecto's Request para BLAME!)
        # res = re.sub(r'\(.*?\)', '', res, flags=re.DOTALL)
        return res.strip()

    # 1. Identify all tags in ORIGINAL text to avoid index mismatch
    patterns = {
        'wrapped': re.compile(r'\[\s*(SUB|TITLE)(?::\s*(.*?))?\s*\](.*?)\s*\[\s*/\1\s*\]', re.IGNORECASE | re.DOTALL),
        'silent_wrapped': re.compile(r'\[\s*SUB:S\s*\](.*?)\s*\[\s*/SUB\s*\]', re.IGNORECASE | re.DOTALL),
        'simple': re.compile(r'\[\s*(SUB|TITLE)\s*:\s*(.*?)\s*\]', re.IGNORECASE),
        'dyn': re.compile(r'\[\s*DYN\s*\](.*?)\s*\[\s*/DYN\s*\]', re.IGNORECASE | re.DOTALL)
    }

    all_tags = []
    for t_type, pattern in patterns.items():
        for m in pattern.finditer(text):
            tag_info = {
                'start': m.start(),
                'end': m.end(),
                'type': t_type,
                'length': m.end() - m.start()
            }
            if t_type == 'wrapped' or t_type == 'silent_wrapped':
                tag_info['tag_name'] = m.group(1).upper() if t_type == 'wrapped' else 'SUB:S'
                tag_info['param'] = (m.group(2) if t_type == 'wrapped' else "").strip()
                tag_info['content'] = (m.group(3) if t_type == 'wrapped' else m.group(1)).strip()
            elif t_type == 'simple':
                tag_info['tag_name'] = m.group(1).upper()
                tag_info['content'] = m.group(2).strip()
            else: # dyn
                tag_info['tag_name'] = 'DYN'
                tag_info['content'] = m.group(1).strip()
            
            all_tags.append(tag_info)
            
    # Sort and remove overlaps
    all_tags.sort(key=lambda x: (int(x['start']), -int(x['length'])))
    tags = []
    last_end = 0
    for t in all_tags:
        t_start = int(t['start'])
        if t_start >= last_end:
            tags.append(t)
            last_end = int(t['end'])
            
    # 2. Build subtitles by parsing each chunk
    last_idx = 0
    raw_subs_unfiltered = []
    scene_highlights = []
    fonetica_full_parts = []
    fonetica_offset = 0 
    
    # helper for sub-chunking (v28.1.5: Added style support)
    def _add_sub(text, f_part, is_dyn, offset, is_highlight=False, y_position=None, style=None):
        p_words = f_part.split()
        d_words = text.split()
        
        # v17.3.2: Sub-chunking (Limit to 10 words for better readability)
        limit = 10
        if len(d_words) > 11: # Threshold to trigger split
            # We need to distribute phonetic words proportionally
            # but since we already parsed, we use simple ratio
            ratio = len(p_words) / len(d_words)
            
            for i in range(0, len(d_words), limit):
                chunk_d = d_words[i : i + limit]
                # estimate phonetic words for this chunk
                start_p = int(i * ratio)
                end_p = int((i + limit) * ratio) if (i + limit) < len(d_words) else len(p_words)
                chunk_p = p_words[start_p : end_p]
                
                raw_subs_unfiltered.append({
                    "text": " ".join(chunk_d),
                    "offset": offset + start_p,
                    "word_count": len(chunk_d),
                    "phonetic_count": len(chunk_p),
                    "is_dynamic": is_dyn,
                    "is_highlight": is_highlight,
                    "y_position": y_position, # v27.8: Chunk inheritance
                    "style": style # v28.1.5: Persistent Style
                })
        else:
            raw_subs_unfiltered.append({
                "text": text,
                "offset": offset,
                "word_count": len(d_words),
                "phonetic_count": len(p_words),
                "is_dynamic": is_dyn,
                "is_highlight": is_highlight,
                "y_position": y_position, # v27.8: Legacy inheritance
                "style": style # v28.1.5: Persistent Style
            })

    for tag in tags:
        # Literal text before tag
        before_raw = text[last_idx:tag['start']]
        if before_raw.strip():
            f_part, d_part, h_list = parse_escena(before_raw)
            clean_text = _cleanup(d_part.strip())

            # v17.3.1: Only add sub if force_dynamic is True (Opt-in logic)
            if force_dynamic and clean_text:
                _add_sub(clean_text, f_part, force_dynamic, fonetica_offset, y_position=None)
            
            # Add highlights
            for h in h_list:
                h['offset'] = int(h.get('offset', 0)) + int(fonetica_offset)
                scene_highlights.append(h)
                
            # v17.3: Clean f_part before counting words to match TTS output (ignores [PAUSA], [TENSO], etc.)
            f_part_clean = re.sub(r'\[.*?\]', '', f_part)
            f_part_clean = re.sub(r'\(.*?\)', '', f_part_clean)
            fonetica_offset += len(f_part_clean.split())
            fonetica_full_parts.append(f_part_clean)
        
        # Tag content
        content_raw = tag.get('content', '')
        
        # v18.7: Support for [SUB: count | text] and [TITLE: count | text] syntax
        # If count is provided, it overrides phonetic_count to control subtitle stay-duration
        p_count_override = None
        # v28.1.9: Initialize overrides to prevent UnboundLocalError
        style_override = None
        y_pos_override = None
        tag_name = tag.get('tag_name', 'SUB')
        
        if tag_name == 'TITLE':
            # v26.7: Restore Title Logic (Top Placement)
            y_pos_override = 0.15
            is_highlight_tag = True
            
            # v27.2: Titles stay longer by default (60 phonetic units ~ 4-5s) if not specified
            if p_count_override is None:
                p_count_override = 60
        else:
            # SUB or DYN
            is_highlight_tag = True if tag['type'] == 'simple' else False
            # v28.1.5: 'SUB' simple tags are treated as Orange Headers at y=0.65
            if tag_name == 'SUB' and tag['type'] == 'simple':
                style_override = 'Header'
                y_pos_override = 0.65 # Sligthly above normal subs
            else:
                style_override = None
                y_pos_override = None 
        display_text = content_raw
        
        # v28.1: Silent tags [SUB:S] or [SUB:S | text] should NOT be narrated
        is_silent_tag = (tag_name == 'SUB:S' or (tag_name == 'SUB' and tag.get('param', '').upper() == 'S'))
        
        # v36.3: UNIFIED PARAMETER PARSER (Universal Meta-Stripper)
        # We now look for parameters in BOTH the content (simple tags with |) 
        # and the tag header (wrapped tags param field).
        params_to_parse = []
        
        if '|' in content_raw and tag['type'] == 'simple':
            p_parts = content_raw.split('|', 1)
            params_to_parse = [p.strip() for p in p_parts[0].split(':')]
            display_text = p_parts[1].strip()
        elif tag['type'] == 'wrapped' and tag.get('param'):
            # [SUB: 0.15] Contenido [/SUB] -> param is "0.15"
            params_to_parse = [p.strip() for p in tag['param'].split(':')]
            display_text = content_raw # Keep original content
        
        # Parse all detected parameters (Order Independent)
        for p in params_to_parse:
            lc = p.lower()
            if lc in ['h', 'highlight', 'resaltado']:
                is_highlight_tag = True
            elif '.' in p:
                try: y_pos_override = float(p)
                except: pass
            else:
                try: p_count_override = int(p)
                except: pass

        f_part, d_part, h_list = parse_escena(display_text)
        is_dyn = tag['type'] == 'dyn'
        
        # v18.7.1: Apply override if exists
        sub_info = {
            "text": _cleanup(d_part),
            "f_part": f_part,
            "is_dyn": is_dyn or force_dynamic,
            "offset": fonetica_offset,
            "y_position": y_pos_override, # v19.6
            "style": style_override # v28.1.5
        }
        
        # helper handles the raw_subs_unfiltered append
        _add_sub(sub_info["text"], sub_info["f_part"], sub_info["is_dyn"], sub_info["offset"], 
                 is_highlight=is_highlight_tag, y_position=y_pos_override, style=style_override)
        
        # Propagate custom Y position to the last added sub
        if raw_subs_unfiltered:
            raw_subs_unfiltered[-1]["y_position"] = y_pos_override
        
        # v18.7.2: Force phonetic_count if override was valid
        if p_count_override is not None and raw_subs_unfiltered:
            raw_subs_unfiltered[-1]["phonetic_count"] = p_count_override
        
        for h in h_list:
            h['offset'] = int(h.get('offset', 0)) + int(fonetica_offset)
            scene_highlights.append(h)
            
        # v17.3: Clean f_part before counting words to match TTS output
        # v18.1 FIX: Simple tags [SUB: Header] or Wrapped [TITLE] tags should NOT be narrated
        # v27.6: Silencing BOTH simple and wrapped TITLE tags from TTS
        should_narrate = True
        if tag['type'] == 'simple' or tag.get('tag_name') == 'TITLE':
            should_narrate = False
            
        if is_silent_tag:
            # v28.1: Preserve [SUB:S] tag for the audio segmenter
            fonetica_full_parts.append(f"[SUB:S]{_cleanup(display_text)}[/SUB]")
            # We don't increment fonetica_offset here because the faked timings 
            # will be handled inside generate_audio_edge relative to the current_time
            should_narrate = False

        if should_narrate:
            f_part_clean = re.sub(r'\[.*?\]', '', f_part)
            f_part_clean = re.sub(r'\(.*?\)', '', f_part_clean)
            fonetica_offset += len(f_part_clean.split())
            fonetica_full_parts.append(f_part_clean)
        
        last_idx = tag['end']
        
    # Final piece
    rest_raw = text[last_idx:]
    if rest_raw.strip():
        f_part, d_part, h_list = parse_escena(rest_raw)
        clean_text = _cleanup(d_part.strip())

        # v17.3.1: Only add sub if force_dynamic is True (Opt-in logic)
        if force_dynamic and clean_text:
            _add_sub(clean_text, f_part, force_dynamic, fonetica_offset, y_position=None)
        
        for h in h_list:
            h['offset'] = int(h.get('offset', 0)) + int(fonetica_offset)
            scene_highlights.append(h)
        
        # v17.3: Clean f_part (Unified)
        f_part_clean = re.sub(r'\[.*?\]', '', f_part)
        f_part_clean = re.sub(r'\(.*?\)', '', f_part_clean)
        fonetica_offset += len(f_part_clean.split())
        fonetica_full_parts.append(f_part_clean)

    # 3. Add highlights as extra subtitles at y=0.35
    raw_subs = [s for s in raw_subs_unfiltered]
    for h in scene_highlights:
        raw_subs.append({
            "text": _cleanup(h["text"]), # v17.2.21: Cleanup highlights too
            "offset": h["offset"],
            "word_count": len(h["text"].split()),
            "phonetic_count": len(h["text"].split()), # v19.6: consistency
            "is_dynamic": False,
            "is_highlight": True,
            "y_position": 0.35
        })
    
    fonetica_final = ' '.join(fonetica_full_parts)
    return fonetica_final.strip(), raw_subs

def parse_avgl_json(json_text):
    data = None
    try:
        data = json.loads(json_text)
    except:
        if '|' in json_text: data = convert_text_to_avgl_json(json_text)
        else: raise ValueError("Invalid Script Format")
    
    script = AVGLScript(title=data.get("title", "Video Sin Título"))
    script.voice = data.get("voice") or data.get("voice_id") or "es-ES-AlvaroNeural"
    script.speed = parse_speed(data.get("speed") or data.get("voice_speed"))
    script.style = data.get("style", "neutral")
    script.background_music = data.get("background_music")
    script.music_volume = float(data.get("music_volume", 0.18))
    # v7.5 Metadata
    script.fuentes = data.get("fuentes", "")
    script.tags = data.get("tags", "")
    script.hashtags = data.get("hashtags", "")
    script.thumbnail = data.get("thumbnail") # v11.36: Cover Injection
    script.music_volume_lock = data.get("music_volume_lock", False)
    # v11.8: General settings pass-through
    script.settings = data.get("settings", {})
    
    for block_data in data.get("blocks", []):
        try: b_vol = float(block_data.get("volume", 0.2))
        except: b_vol = 0.2
        block = AVGLBlock(
            title=block_data.get("title", "Bloque"), 
            music=block_data.get("music"), 
            volume=b_vol
        )
        # Block-level Voice Overrides
        block.voice = block_data.get("voice")
        block.voice_speed = parse_speed(block_data.get("voice_speed")) if block_data.get("voice_speed") else None
        
        for s_data in block_data.get("scenes", []):
            scene = AVGLScene(title=s_data.get("title", "Escena"))
            scene.text = str(s_data.get("text") or s_data.get("voice") or "")
            scene.voice = s_data.get("voice") or script.voice
            scene.speed = parse_speed(s_data.get("speed")) if s_data.get("speed") else script.speed
            scene.pitch = s_data.get("pitch")
            try: scene.pause = float(s_data.get("pause", 0.0))
            except: scene.pause = 0.0
            
            # v20.4: Manual Duration Override
            try: scene.duration = float(s_data.get("duration", 0.0))
            except: scene.duration = 0.0
            scene.force_duration = s_data.get("force_duration", False)
            
            scene.subtitle = s_data.get("subtitle", "")
            scene.audio = s_data.get("audio") # v5.3: Custom Audio Support
            scene.lipsync = s_data.get("lipsync", False) # v9.0
            scene.language = s_data.get("language") # v5.1
            scene.dubbing_mode = s_data.get("dubbing_mode") # v5.1
            scene.silent = s_data.get("silent", False) # v28.0
            
            # v28.1: Tag-based Silent Mode (Global Scene)
            if "[silencio]" in scene.text.lower() or "[sub:s]" in scene.text.lower():
                # Note: if [sub:s] is used alone as a tag, it can silence the whole scene.
                # However, if it's used as a wrapper, generate_audio_edge will handle partial silence.
                # But if the user just wants the whole scene silent, [silencio] is the way.
                # For compatibility, if [silencio] is found, we set scene.silent = True.
                if "[silencio]" in scene.text.lower():
                    scene.silent = True
            
            force_dynamic = data.get("dynamic_subtitles", False)
            clean_txt, extracted_subs = extract_subtitles_v35(scene.text, force_dynamic=force_dynamic)
            scene.text = clean_txt
            scene.subtitles = extracted_subs or s_data.get("subtitles", [])
            
            # v35.5: Unified Layer Logic
            # Support both legacy 'assets' list and modern 'layers' structure from Visual Editor
            raw_assets = s_data.get("assets", [])
            layers = s_data.get("layers", {})
            if layers and layers.get("background"):
                # Avoid duplicates if it's already in the assets list
                bg_data = layers["background"]
                bg_id = bg_data.get("id") or bg_data.get("type")
                if not any((getattr(a, 'id', None) == bg_id or getattr(a, 'type', None) == bg_id) for a in scene.assets):
                    raw_assets.append(bg_data)

            for a_data in raw_assets:
                if isinstance(a_data, str): scene.assets.append(AVGLAsset(a_data))
                else: 
                    # v15.1: Robust Path Detection (id vs type)
                    target_id = a_data.get("id")
                    if not target_id or target_id in ['video', 'image']:
                        target_id = a_data.get("type")
                    
                    scene.assets.append(AVGLAsset(
                        target_id, 
                        a_data.get("zoom"), 
                        a_data.get("move"), 
                        a_data.get("overlay"), 
                        a_data.get("fit", False),
                        shake=a_data.get("shake", False) or a_data.get("shake_intensity", 0) > 0,
                        rotate=a_data.get("rotate"),
                        shake_intensity=a_data.get("shake_intensity", 5),
                        w_rotate=a_data.get("w_rotate"),
                        video_volume=a_data.get("video_volume"),
                        fast_assembly=a_data.get("fast_assembly", False),
                        cinema_mode=a_data.get("cinema_mode", False),
                        start_time=safe_float(a_data.get("start_time"), 0.0),
                        end_time=safe_float(a_data.get("end_time"), None) if a_data.get("end_time") is not None else None
                    ))
            
            for sfx_data in s_data.get("sfx", []):
                if isinstance(sfx_data, str): scene.sfx.append(AVGLSFX(sfx_data))
                else: 
                    try: vol = float(sfx_data.get("volume", 0.5))
                    except: vol = 0.5
                    scene.sfx.append(AVGLSFX(sfx_data.get("type") or sfx_data.get("id"), vol, int(sfx_data.get("offset", 0))))
            
            block.scenes.append(scene)

        for group in block_data.get("groups", []):
            master_asset = group.get("master_asset")
            group_master_audio = group.get("audio") # v11.0 Performance Mode
            group_id = f"g_{id(group)}"
            
            for s_data in group.get("scenes", []):
                scene = AVGLScene(title=s_data.get("title", "Escena"))
                scene.group_id = group_id
                scene.group_settings = group
                scene.text = str(s_data.get("text") or s_data.get("voice") or "")
                scene.voice = s_data.get("voice") or script.voice
                scene.speed = parse_speed(s_data.get("speed")) if s_data.get("speed") else script.speed
                scene.pitch = s_data.get("pitch")
                scene.pause = s_data.get("pause", 0.0)
                
                # v20.4: Manual Duration Override (Groups)
                try: scene.duration = float(s_data.get("duration", 0.0))
                except: scene.duration = 0.0
                scene.force_duration = s_data.get("force_duration", False)
                
                scene.subtitle = s_data.get("subtitle", "")
                scene.audio = s_data.get("audio") or group_master_audio
                scene.language = s_data.get("language") # v5.1
                scene.dubbing_mode = s_data.get("dubbing_mode") # v5.1
                
                clean_txt, extracted_subs = extract_subtitles_v35(scene.text)
                scene.text = clean_txt
                scene.subtitles = extracted_subs or s_data.get("subtitles", [])

                # Inheritance from Group Master Asset (v14.5 Refined)
                raw_assets = s_data.get("assets", [])
                layers = s_data.get("layers", {})
                if layers and layers.get("background"):
                     raw_assets.append(layers["background"])

                if not raw_assets and master_asset:
                    raw_assets = [master_asset]
                
                for a_data in raw_assets:
                    if isinstance(a_data, str):
                        scene.assets.append(AVGLAsset(a_data))
                    else:
                        # v14.7: Clearer inheritance. Ignore 'video'/'image' as valid IDs.
                        target_id = a_data.get("id")
                        if (not target_id or target_id in ['video', 'image']) and master_asset:
                            target_id = master_asset if isinstance(master_asset, str) else (master_asset.get("id") or master_asset.get("type"))
                        
                        scene.assets.append(AVGLAsset(
                            target_id, 
                            a_data.get("zoom"), 
                            a_data.get("move"), 
                            a_data.get("overlay"), 
                            a_data.get("fit", False),
                            shake=a_data.get("shake", False) or a_data.get("shake_intensity", 0) > 0,
                            rotate=a_data.get("rotate"),
                            shake_intensity=a_data.get("shake_intensity", 5),
                            w_rotate=a_data.get("w_rotate"),
                            video_volume=a_data.get("video_volume"),
                            fast_assembly=a_data.get("fast_assembly", False),
                            start_time=safe_float(a_data.get("start_time"), 0.0),
                            end_time=safe_float(a_data.get("end_time"), None) if a_data.get("end_time") is not None else None
                        ))

                for sfx_data in s_data.get("sfx", []):
                    if isinstance(sfx_data, str): scene.sfx.append(AVGLSFX(sfx_data))
                    else: 
                        sfx_vol = sfx_data.get("volume")
                        if sfx_vol is None: sfx_vol = 0.5
                        sfx_off = sfx_data.get("offset")
                        if sfx_off is None: sfx_off = 0
                        scene.sfx.append(AVGLSFX(sfx_data.get("type") or sfx_data.get("id"), float(sfx_vol), int(sfx_off)))
                
                block.scenes.append(scene)

        script.blocks.append(block)
    return script

def translate_emotions(text, use_ssml=False):
    """
    v17.3: Devuelve el texto limpio. Las emociones ahora se manejan por segmentación
    en generate_audio_edge para evitar el escape de SSML de edge-tts 7.x.
    """
    if not use_ssml: return text
    # Simplemente limpiamos las etiquetas si se pide limpieza, 
    # la lógica real de aplicación ahora está en la segmentación.
    clean = re.sub(r'\[/?(?:TENSO|EPICO|SUSPENSO|GRITANDO|SUSURRO)\]', '', text, flags=re.IGNORECASE)
    return clean

def wrap_ssml(text, voice, speed="+0%", pitch=None):
    """
    DEPRECATED v17.3: edge-tts 7.x escapa todo el texto enviado a Communicate,
    haciendo imposible el envío de SSML manual sin que se lea literalmente.
    """
    return text

# ═══════════════════════════════════════════════════════════════════
# Audio Generation (Edge TTS & ElevenLabs)
# ═══════════════════════════════════════════════════════════════════


async def generate_audio_edge(text, output_path, voice="es-DO-EmilioNeural", rate="+0%", pitch="+0Hz", scene=None):
    """
    Robust Segmented Engine (v17.3)
    Splits by [PAUSA:X.X] AND Emotions [TAG]...[/TAG].
    Since edge-tts escapes SSML, we must physically split audio and join it.
    """
    import edge_tts
    
    emotions_map = {
        'TENSO': {'pitch': '-2Hz', 'rate': '-5%'},
        'EPICO': {'pitch': '+5Hz', 'rate': '+10%'},
        'SUSPENSO': {'pitch': '-5Hz', 'rate': '-25%'},
        'GRITANDO': {'pitch': '+15Hz', 'rate': '+20%'},
        'SUSURRO': {'pitch': '-4Hz', 'rate': '-10%'},
    }

    # v17.3: Unified Segmentation (Pauses + Emotions)
    # Regex perrona que atrapa [PAUSA:X] o [TAG]...[/TAG]
    # Atrapamos el contenido de las emociones para procesarlo con sus settings
    segments = []
    
    # Primero extraemos las foneticas reales
    fonetica_raw, _, _ = parse_escena(text)
    
    # Buscamos etiquetas de emocion: [TAG]contenido[/TAG]
    # pattern = r'(\[PAUSA:[\d\.]+\]|\[(PHO|SFX|BOX|SUB|TITLE|SUB:.*?|TITLE:.*?|PHO:.*?)\]|\[(?:TENSO|EPICO|SUSPENSO|GRITANDO|SUSURRO)\].*?\[/(?:TENSO|EPICO|SUSPENSO|GRITANDO|SUSURRO)\])'
    # v28.1: Added SUB:S to pattern for partial silence
    pattern = r'(\[PAUSA:[\d\.]+\]|\[SUB:S\].*?\[/SUB\]|\[(PHO|SFX|BOX|SUB|TITLE|SUB:.*?|TITLE:.*?|PHO:.*?)\]|\[(?:TENSO|EPICO|SUSPENSO|GRITANDO|SUSURRO)\].*?\[/(?:TENSO|EPICO|SUSPENSO|GRITANDO|SUSURRO)\])'
    parts = re.split(pattern, fonetica_raw, flags=re.IGNORECASE | re.DOTALL)
    
    for part in parts:
        if not part: continue
        
        # ¿Es una pausa?
        pause_match = re.match(r'\[PAUSA:([\d\.]+)\]', part, re.IGNORECASE)
        if pause_match:
            segments.append(('pause', float(pause_match.group(1)), {}))
            continue
            
        # v28.1: ¿Es un subtítulo silente?
        silent_match = re.match(r'\[SUB:S\](.*?)\[/SUB\]', part, re.IGNORECASE | re.DOTALL)
        if silent_match:
            silent_text = silent_match.group(1).strip()
            if silent_text:
                # Duración estimada: 2.5 palabras/seg (Mínimo 1s)
                dur = max(1.0, len(silent_text.split()) / 2.5)
                segments.append(('silent_sub', silent_text, {'duration': dur}))
            continue
            
        # ¿Es una emoción?
        emo_match = re.match(r'\[(TENSO|EPICO|SUSPENSO|GRITANDO|SUSURRO)\](.*?)\[/\1\]', part, re.IGNORECASE | re.DOTALL)
        if emo_match:
            emo_tag = emo_match.group(1).upper()
            emo_text = emo_match.group(2).strip()
            if emo_text:
                segments.append(('text', emo_text, emotions_map.get(emo_tag, {})))
            continue
            
        # Es texto normal (o restos)
        clean_text = re.sub(r'\[.*?\]', '', part).strip()
        if clean_text:
            segments.append(('text', clean_text, {}))

    if not segments:
        # v28.1.10: Tag-only scenes or empty text should return a tiny silence 
        # instead of False to avoid "Error generating audio" alerts.
        from moviepy import AudioClip
        silent_clip = AudioClip(lambda t: 0, duration=0.1)
        silent_clip.write_audiofile(output_path, fps=44100, logger=None)
        silent_clip.close()
        return True
    
    audio_clips = []
    temp_files = []
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_segments')
    os.makedirs(temp_dir, exist_ok=True)
    prefix = f"seg_{int(time.time())}_{random.randint(100,999)}"
    current_time = 0.0
    voice_intervals = []
    
    try:
        for i, (tag, val, settings_emo) in enumerate(segments):
            if tag == 'pause':
                silence = AudioClip(lambda t: np.zeros(2), duration=val).with_fps(44100)
                audio_clips.append(silence)
                current_time += val
            elif tag == 'silent_sub':
                # v28.1: Inyectar silencio y finguir word_timings para que los subtítulos aparezcan
                dur = settings_emo.get('duration', 1.0)
                silence = AudioClip(lambda t: np.zeros(2), duration=dur).with_fps(44100)
                audio_clips.append(silence)
                
                if scene:
                    words = val.split()
                    if words:
                        time_per_word = dur / len(words)
                        for idx, w in enumerate(words):
                            scene.word_timings.append({
                                "start": current_time + (idx * time_per_word),
                                "end": current_time + ((idx + 1) * time_per_word),
                                "word": w
                            })
                current_time += dur
            else:
                seg_path = os.path.join(temp_dir, f"{prefix}_{i}.mp3")
                temp_files.append(seg_path)
                
                # Combinar settings base con los de la emocion
                seg_rate = settings_emo.get('rate', rate)
                seg_pitch = settings_emo.get('pitch', pitch)
                
                # v17.3: Clean all visual tags before TTS
                clean = re.sub(r'(?i)\[(ZOOM|MOVE|FIT|AUDIO|SFX|PAN|VOICE|PITCH|TITLE|INSTRUCCIÓN|INSTRUCTION|SUB).*?\]', '', val)
                clean = re.sub(r'\[.*?\]', '', clean) # Residuals
                clean = re.sub(r'\(.*?\)', '', clean) # Comments
                clean = clean.strip()
                
                if not clean: continue

                communicate = edge_tts.Communicate(clean, voice, rate=seg_rate, pitch=seg_pitch)

                # v16.5: Stream to capture word boundaries
                last_word_end = 0.0
                with open(seg_path, "wb") as f:
                    async for event in communicate.stream():
                        e_type = event.get("type", "").lower()
                        if e_type == "audio":
                            f.write(event["data"])
                        elif e_type in ["wordboundary", "word_boundary"]:
                            if scene:
                                start_s = event["offset"] / 10_000_000
                                dur_s = event["duration"] / 10_000_000
                                end_s = start_s + dur_s
                                last_word_end = max(last_word_end, end_s)
                                
                                scene.word_timings.append({
                                    "start": current_time + start_s,
                                    "end": current_time + end_s,
                                    "word": event["text"]
                                })
                        elif e_type in ["sentenceboundary", "sentence_boundary"]:
                            # Fallback: Interpolate words if no WordBoundaries are emitted
                            if scene and not any(wt['start'] >= current_time + (event["offset"]/10_000_000) for wt in scene.word_timings):
                                s_text = event.get("text", "")
                                s_words = s_text.split()
                                if s_words:
                                    s_start_s = event["offset"] / 10_000_000
                                    s_dur_s = event["duration"] / 10_000_000
                                    w_dur = s_dur_s / len(s_words)
                                    last_word_end = max(last_word_end, s_start_s + s_dur_s)
                                    
                                    for idx, word in enumerate(s_words):
                                        scene.word_timings.append({
                                            "start": current_time + s_start_s + (idx * w_dur),
                                            "end": current_time + s_start_s + ((idx + 1) * w_dur),
                                            "word": word
                                        })
                
                if os.path.exists(seg_path):
                    try:
                        clip = AudioFileClip(seg_path)
                        
                        # v26.8 FINETUNING: Recorte Exacto basado en Timestamps
                        # En lugar de adivinar el padding, usamos el último timestamp real.
                        # Si last_word_end > 0, sabemos donde termina la voz.
                        # ELIMINADO EL MARGEN 0.1s para reducir desfase.
                        if last_word_end > 0:
                            # Use exact end time, no buffer
                            new_duration = min(clip.duration, last_word_end)
                            if new_duration < clip.duration:
                                clip = clip.with_duration(new_duration)
                        
                        voice_intervals.append((current_time, current_time + clip.duration))
                        audio_clips.append(clip)
                        # REMOVED PREMATURE UPDATE: current_time += clip.duration
                    except Exception as e:
                        print(f"Error loading audio segment: {e}")

                # v26.10: Auto-Calibration for Speed/Sync Drift
                # If audio is faster than TTS timestamps (common with rate changes),
                # we scale the word timings to match the actual audio duration.
                # This fixes internal drift within the segment.
                if last_word_end > 0 and audio_clips:
                    actual_duration = audio_clips[-1].duration
                    # Tolerance: Only scale if mismatch is significant (>1% or >20ms)
                    if actual_duration < (last_word_end - 0.02): # Audio is shorter/faster
                        scale_factor = actual_duration / last_word_end
                        
                        # Apply scaling to the WORDS we just added for this segment.
                        # Since current_time hasn't been updated yet, these words start >= current_time.
                        for wt in scene.word_timings:
                            if wt['start'] >= current_time:
                                # Relativize, Scale, Absolutize
                                rel_start = wt['start'] - current_time
                                rel_end = wt['end'] - current_time
                                
                                wt['start'] = current_time + (rel_start * scale_factor)
                                wt['end'] = current_time + (rel_end * scale_factor)

                if audio_clips:
                     current_time += audio_clips[-1].duration

        if audio_clips:
            final_audio = concatenate_audioclips(audio_clips)
            final_audio.write_audiofile(output_path, logger=None)
            for clip in audio_clips: clip.close()
            for f in temp_files:
                try: os.remove(f)
                except: pass
            if scene:
                scene.voice_intervals = voice_intervals
            return True
        return False
    except Exception as e:
        print(f"❌ Error Audio v5.2: {e}")
        return False

async def generate_audio_elevenlabs(text, output_path, voice_id, api_key):
    """
    v35.1: Robust ElevenLabs API (SDK-Less)
    Uses direct requests to bypass SDK/Pydantic incompatibilities with Python 3.14.
    """
    import requests
    import json
    try:
        clean_text = re.sub(r'<[^>]+>', '', text)
        clean_text = re.sub(r'\[.*?\]', '', clean_text).strip()
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key.strip() if api_key else ""
        }
        data = {
            "text": clean_text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            return True
        else:
            # v35.2: Specific logic for Permission Error (Account/Subscription issue)
            if "missing_permissions" in response.text:
                print(f"❌ ElevenLabs [PERMISSIONS]: La API Key no tiene permiso de 'text_to_speech'.")
                print(f"   Tip: Revisa tu suscripción o crea una nueva key con todos los permisos en ElevenLabs.")
            else:
                print(f"❌ ElevenLabs Error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error ElevenLabs v35.1: {e}")
        return False

def convert_text_to_avgl_json(text_script, title="Nuevo Video"):
    script = {"title": title, "blocks": []}
    lines = text_script.strip().split('\n')
    current_block = {"title": "Capítulo Principal", "scenes": [], "groups": []}
    current_group = None

    for line in lines:
        raw_line = line.strip()
        if not raw_line: continue
        
        # Metadata
        if raw_line.startswith('#'):
            low_line = raw_line.lower()
            if 'título:' in low_line: script["title"] = raw_line.split(':', 1)[1].strip()
            elif 'fuentes:' in low_line: script["fuentes"] = raw_line.split(':', 1)[1].strip()
            elif 'tags:' in low_line: script["tags"] = raw_line.split(':', 1)[1].strip()
            elif 'hashtags:' in low_line: script["hashtags"] = raw_line.split(':', 1)[1].strip()
            continue
            
        # Blocks
        if raw_line.startswith('---') and raw_line.endswith('---'):
            if current_block["scenes"] or current_block["groups"]: 
                script["blocks"].append(current_block)
            current_block = {"title": raw_line.replace('-', '').strip(), "scenes": [], "groups": []}
            current_group = None
            continue

        # Group Start: === GRUPO: asset | instructions ===
        if raw_line.startswith('=== GRUPO:'):
            g_content = raw_line.replace('=== GRUPO:', '').replace('===', '').strip()
            g_parts = [p.strip() for p in g_content.split('|')]
            m_asset = g_parts[0] if g_parts else "negro.png"
            
            current_group = {
                "title": "Master Shot",
                "master_asset": m_asset,
                "scenes": []
            }
            
            # Parse Group Instructions
            if len(g_parts) > 1:
                g_instr = g_parts[1].upper()
                if 'ZOOM:' in g_instr:
                    z = re.search(r'ZOOM:([\d\.]+):([\d\.]+)', g_instr)
                    if z: current_group["zoom"] = f"{z.group(1)}:{z.group(2)}"
                if 'MOVE:' in g_instr:
                    # Move can be HOR:0:100 + VER:50:50
                    m = re.search(r'MOVE:(.*?)(?: \||$)', g_instr)
                    if m: current_group["move"] = m.group(1).strip()
                if 'FIT' in g_instr: current_group["fit"] = True
                
            continue

        # Group End
        if raw_line.startswith('=== FIN GRUPO'):
            if current_group:
                current_block["groups"].append(current_group)
                current_group = None
            continue

        # Scene: TITLE | asset | instructions | pause | text
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 3:
            asset_id = parts[1]
            instr = parts[2].upper()
            
            scene = {"title": parts[0], "text": parts[-1], "assets": []}
            
            # Asset Logic
            if asset_id and asset_id != "negro.png":
                asset_obj = {"id": asset_id}
                if 'ZOOM:' in instr:
                    z = re.search(r'ZOOM:([\d\.]+):([\d\.]+)', instr)
                    if z: asset_obj["zoom"] = f"{z.group(1)}:{z.group(2)}"
                if 'FIT' in instr: asset_obj["fit"] = True
                if 'MOVE:' in instr:
                    m = re.search(r'MOVE:(.*?)(?: \||$)', instr)
                    if m: asset_obj["move"] = m.group(1).strip()
                scene["assets"].append(asset_obj)
            
            if len(parts) >= 5:
                try: scene["pause"] = float(parts[4])
                except: pass
            
            # v27.7: Parse SFX from text [SFX:file:vol:off]
            sfx_matches = re.findall(r'\[SFX:(.*?)\]', scene["text"])
            if sfx_matches:
                if "sfx" not in scene: scene["sfx"] = []
                for match in sfx_matches:
                    sfx_parts = match.split(':')
                    s_type = sfx_parts[0]
                    s_vol = float(sfx_parts[1]) if len(sfx_parts) > 1 else 0.5
                    s_off = int(sfx_parts[2]) if len(sfx_parts) > 2 else 0
                    scene["sfx"].append({"type": s_type, "volume": s_vol, "offset": s_off})
                # Clean text from SFX tags
                scene["text"] = re.sub(r'\[SFX:.*?\]', '', scene["text"]).strip()
            
            if current_group is not None:
                current_group["scenes"].append(scene)
            else:
                current_block["scenes"].append(scene)
            
    if current_block["scenes"] or current_block["groups"]: 
        script["blocks"].append(current_block)
    return script

def convert_avgl_json_to_text(data):
    """
    Reverse conversion: JSON -> Legacy Pipe-separated Text.
    v8.1: Handles metadata and scene blocks.
    """
    lines = []
    
    # 1. Global Metadata
    if data.get("title") and data.get("title") != "Video Sin Título":
        lines.append(f"# TÍTULO: {data['title']}")
        
    if data.get("fuentes"): lines.append(f"# FUENTES: {data['fuentes']}")
    if data.get("tags"): lines.append(f"# TAGS: {data['tags']}")
    if data.get("hashtags"): lines.append(f"# HASHTAGS: {data['hashtags']}")
    
    if lines: lines.append("") # Spacer
    
    # 2. Blocks and Scenes
    for block in data.get("blocks", []):
        block_title = block.get("title", "Bloque")
        lines.append(f"--- {block_title} ---")
        
        # Scenes at block level
        for scene in block.get("scenes", []):
            lines.append(convert_scene_to_line(scene))
            
        # Scenes inside groups
        for group in block.get("groups", []):
            title = group.get("title", "Master Shot")
            m_asset = group.get("master_asset")
            m_id = "negro.png"
            if m_asset:
                m_id = m_asset if isinstance(m_asset, str) else (m_asset.get("id") or m_asset.get("type") or "negro.png")
            
            # Group instructions
            g_instr = []
            if group.get("zoom"): g_instr.append(f"ZOOM:{group['zoom']}")
            if group.get("fit"): g_instr.append("FIT")
            if group.get("move"): g_instr.append(f"MOVE:{group['move']}")
            g_instr_str = " | " + " ".join(g_instr) if g_instr else ""
            
            lines.append(f"=== GRUPO: {m_id}{g_instr_str} ===")
            for scene in group.get("scenes", []):
                lines.append("  " + convert_scene_to_line(scene))
            lines.append("=== FIN GRUPO ===")
        
        lines.append("") # Spacer between blocks
        
    return "\n".join(lines).strip()

def convert_scene_to_line(scene):
    title = scene.get("title", "Escena")
    text = scene.get("text") or scene.get("voice") or ""
    
    # Asset logic
    asset_name = "" # v16.7.6: Default to empty for better synchronization
    asset_instr = ""
    
    # Support both 'assets' (list) and 'asset' (single string/object)
    assets_list = scene.get("assets")
    if not assets_list and scene.get("asset"):
        assets_list = [scene.get("asset")]
        
    if assets_list and len(assets_list) > 0:
        asset = assets_list[0]
        if isinstance(asset, str):
            asset_name = asset
        else:
            asset_name = asset.get("id") or asset.get("type") or ""
        
        # Instructions (Zoom/Fit/Move)
        instr_parts = []
        if isinstance(asset, dict):
            if asset.get("zoom"): instr_parts.append(f"ZOOM:{asset['zoom']}")
            if asset.get("fit"): instr_parts.append("FIT")
            if asset.get("move"): instr_parts.append(f"MOVE:{asset['move']}")
        else:
            # Check if keys are directly in the scene (for flat JSON)
            if scene.get("zoom"): instr_parts.append(f"ZOOM:{scene['zoom']}")
            if scene.get("fit"): instr_parts.append("FIT")
            if scene.get("move"): instr_parts.append(f"MOVE:{scene['move']}")
        
        if instr_parts:
            asset_instr = " ".join(instr_parts)
    
    pause = scene.get("pause", 0.0)
    
    # v27.7: Include SFX in text format [SFX:file:vol:off]
    sfx_tags = ""
    for s_item in scene.get("sfx", []):
        s_type = s_item.get("type") or s_item.get("id") or ""
        s_vol = s_item.get("volume", 0.5)
        s_off = s_item.get("offset", 0)
        sfx_tags += f" [SFX:{s_type}:{s_vol}:{s_off}]"

    # Format: TITLE | asset.png | instructions | pause | text
    # Instructions can be empty now
    return f"{title} | {asset_name} | {asset_instr} | {pause} | {text}{sfx_tags}"
