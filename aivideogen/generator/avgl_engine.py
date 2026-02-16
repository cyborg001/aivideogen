import os
import asyncio
import random
import json
import re
import time
from django.conf import settings
from moviepy import AudioFileClip, concatenate_audioclips, AudioClip
import numpy as np

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
    def __init__(self, asset_type, zoom=None, move=None, overlay=None, fit=False, shake=False, rotate=None, shake_intensity=5, w_rotate=None, video_volume=None):
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
        # Remove parentheses for extra safety
        res = re.sub(r'\(.*?\)', '', res, flags=re.DOTALL)
        return res.strip()

    # 1. Identify all tags in ORIGINAL text to avoid index mismatch
    patterns = {
        'wrapped': re.compile(r'\[\s*(?:SUB|TITLE)(?::\s*(.*?))?\s*\](.*?)\s*\[\s*/(?:SUB|TITLE)\s*\]', re.IGNORECASE | re.DOTALL),
        'simple': re.compile(r'\[\s*(?:SUB|TITLE)\s*:\s*(.*?)\s*\]', re.IGNORECASE),
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
            if t_type == 'wrapped':
                tag_info['param'] = (m.group(1) or "").strip()
                tag_info['content'] = (m.group(2) or "").strip()
            else:
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
    
    # helper for sub-chunking
    def _add_sub(text, f_part, is_dyn, offset, is_highlight=False):
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
                    "is_highlight": is_highlight
                })
        else:
            raw_subs_unfiltered.append({
                "text": text,
                "offset": offset,
                "word_count": len(d_words),
                "phonetic_count": len(p_words),
                "is_dynamic": is_dyn,
                "is_highlight": is_highlight
            })

    for tag in tags:
        # Literal text before tag
        before_raw = text[last_idx:tag['start']]
        if before_raw.strip():
            f_part, d_part, h_list = parse_escena(before_raw)
            clean_text = _cleanup(d_part.strip())

            f_part, d_part, h_list = parse_escena(before_raw)
            clean_text = _cleanup(d_part.strip())

            # v17.3.1: Only add sub if force_dynamic is True (Opt-in logic)
            if force_dynamic and clean_text:
                _add_sub(clean_text, f_part, force_dynamic, fonetica_offset)
            
            # Add highlights
            for h in h_list:
                h['offset'] = int(h.get('offset', 0)) + int(fonetica_offset)
                scene_highlights.append(h)
                
            # v17.3: Clean f_part before counting words to match TTS output (ignores [PAUSA], [TENSO], etc.)
            f_part_clean = re.sub(r'\[.*?\]', '', f_part)
            f_part_clean = re.sub(r'\(.*?\)', '', f_part_clean)
            fonetica_offset += len(f_part_clean.split())
            fonetica_full_parts.append(f_part)
        
        # Tag content
        content_raw = tag.get('content', '')
        
        # v18.7: Support for [SUB: count | text] and [TITLE: count | text] syntax
        # If count is provided, it overrides phonetic_count to control subtitle stay-duration
        p_count_override = None
        # v19.6: Force highlights and specific Y-pos for titles
        is_highlight_tag = True if tag['type'] == 'simple' else False
        y_pos_override = 0.45 if tag['type'] == 'simple' else 0.70
        display_text = content_raw
        
        if '|' in content_raw and tag['type'] == 'simple':
            p_parts = content_raw.split('|', 1)
            params_raw = p_parts[0].strip()
            display_text = p_parts[1].strip()
            
            # v19.2: Support extended syntax [SUB: count:style | text]
            if ':' in params_raw:
                param_pieces = params_raw.split(':', 1)
                try: p_count_override = int(param_pieces[0].strip())
                except: pass
                
                style_code = param_pieces[1].strip().lower()
                if style_code in ['h', 'highlight', 'resaltado']:
                    is_highlight_tag = True
            else:
                try: p_count_override = int(params_raw)
                except: pass
        
        f_part, d_part, h_list = parse_escena(display_text)
        is_dyn = tag['type'] == 'dyn'
        
        # v18.7.1: Apply override if exists
        sub_info = {
            "text": _cleanup(d_part),
            "f_part": f_part,
            "is_dyn": is_dyn or force_dynamic,
            "offset": fonetica_offset,
            "y_position": y_pos_override # v19.6
        }
        
        # helper handles the raw_subs_unfiltered append
        _add_sub(sub_info["text"], sub_info["f_part"], sub_info["is_dyn"], sub_info["offset"], is_highlight=is_highlight_tag)
        
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
        # v18.1 FIX: Simple tags [SUB: Header] should NOT be narrated (Arquitecto's Request)
        if tag['type'] != 'simple':
            f_part_clean = re.sub(r'\[.*?\]', '', f_part)
            f_part_clean = re.sub(r'\(.*?\)', '', f_part_clean)
            fonetica_offset += len(f_part_clean.split())
            fonetica_full_parts.append(f_part)
        
        last_idx = tag['end']
        
    # Final piece
    rest_raw = text[last_idx:]
    if rest_raw.strip():
        f_part, d_part, h_list = parse_escena(rest_raw)
        clean_text = _cleanup(d_part.strip())

        # v17.3.1: Only add sub if force_dynamic is True (Opt-in logic)
        if force_dynamic and clean_text:
            _add_sub(clean_text, f_part, force_dynamic, fonetica_offset)
        
        for h in h_list:
            h['offset'] = int(h.get('offset', 0)) + int(fonetica_offset)
            scene_highlights.append(h)
        
        # v17.3: Clean f_part (Unified)
        f_part_clean = re.sub(r'\[.*?\]', '', f_part)
        f_part_clean = re.sub(r'\(.*?\)', '', f_part_clean)
        fonetica_offset += len(f_part_clean.split())
        fonetica_full_parts.append(f_part)

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
    script.music_volume_lock = data.get("music_volume_lock", False)
    
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
            scene.pause = s_data.get("pause", 0.0)
            scene.subtitle = s_data.get("subtitle", "")
            scene.audio = s_data.get("audio") # v5.3: Custom Audio Support
            
            force_dynamic = data.get("dynamic_subtitles", False)
            clean_txt, extracted_subs = extract_subtitles_v35(scene.text, force_dynamic=force_dynamic)
            scene.text = clean_txt
            scene.subtitles = extracted_subs or s_data.get("subtitles", [])
            
            for a_data in s_data.get("assets", []):
                if isinstance(a_data, str): scene.assets.append(AVGLAsset(a_data))
                else: scene.assets.append(AVGLAsset(
                    a_data.get("id") or a_data.get("type"), 
                    a_data.get("zoom"), 
                    a_data.get("move"), 
                    a_data.get("overlay"), 
                    a_data.get("fit", False),
                    shake=a_data.get("shake", False),
                    rotate=a_data.get("rotate"),
                    shake_intensity=a_data.get("shake_intensity", 5),
                    w_rotate=a_data.get("w_rotate"),
                    video_volume=a_data.get("video_volume")
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
                scene.subtitle = s_data.get("subtitle", "")
                scene.audio = s_data.get("audio")
                
                clean_txt, extracted_subs = extract_subtitles_v35(scene.text)
                scene.text = clean_txt
                scene.subtitles = extracted_subs or s_data.get("subtitles", [])

                # Inheritance from Group Master Asset (v14.5 Refined)
                raw_assets = s_data.get("assets", [])
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
                            shake=a_data.get("shake", False),
                            rotate=a_data.get("rotate"),
                            shake_intensity=a_data.get("shake_intensity", 5),
                            w_rotate=a_data.get("w_rotate"),
                            video_volume=a_data.get("video_volume")
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
    # v19.6 Support for [TITLE] along with [PHO], [SFX], [BOX], [SUB]
    pattern = r'(\[PAUSA:[\d\.]+\]|\[(PHO|SFX|BOX|SUB|TITLE|SUB:.*?|TITLE:.*?|PHO:.*?)\]|\[(?:TENSO|EPICO|SUSPENSO|GRITANDO|SUSURRO)\].*?\[/(?:TENSO|EPICO|SUSPENSO|GRITANDO|SUSURRO)\])'
    parts = re.split(pattern, fonetica_raw, flags=re.IGNORECASE | re.DOTALL)
    
    for part in parts:
        if not part: continue
        
        # ¿Es una pausa?
        pause_match = re.match(r'\[PAUSA:([\d\.]+)\]', part, re.IGNORECASE)
        if pause_match:
            segments.append(('pause', float(pause_match.group(1)), {}))
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

    if not segments: return False
    
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
                with open(seg_path, "wb") as f:
                    async for event in communicate.stream():
                        e_type = event.get("type", "").lower()
                        if e_type == "audio":
                            f.write(event["data"])
                        elif e_type in ["wordboundary", "word_boundary"]:
                            if scene:
                                start_s = event["offset"] / 10_000_000
                                dur_s = event["duration"] / 10_000_000
                                scene.word_timings.append({
                                    "start": current_time + start_s,
                                    "end": current_time + start_s + dur_s,
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
                                    for idx, word in enumerate(s_words):
                                        scene.word_timings.append({
                                            "start": current_time + s_start_s + (idx * w_dur),
                                            "end": current_time + s_start_s + ((idx + 1) * w_dur),
                                            "word": word
                                        })
                if os.path.exists(seg_path):
                    clip = AudioFileClip(seg_path)
                    voice_intervals.append((current_time, current_time + clip.duration))
                    audio_clips.append(clip)
                    current_time += clip.duration
        
        if scene:
            scene.voice_intervals = voice_intervals

        if audio_clips:
            final_audio = concatenate_audioclips(audio_clips)
            final_audio.write_audiofile(output_path, logger=None)
            for clip in audio_clips: clip.close()
            for f in temp_files:
                try: os.remove(f)
                except: pass
            return True
        return False
    except Exception as e:
        print(f"❌ Error Audio v5.2: {e}")
        return False

async def generate_audio_elevenlabs(text, output_path, voice_id, api_key):
    from elevenlabs.client import ElevenLabs
    from elevenlabs import save
    try:
        clean_text = re.sub(r'<[^>]+>', '', text)
        clean_text = re.sub(r'\[.*?\]', '', clean_text).strip()
        client = ElevenLabs(api_key=api_key)
        audio_gen = client.text_to_speech.convert(text=clean_text, voice_id=voice_id, model_id="eleven_multilingual_v2")
        save(audio_gen, output_path)
        return True
    except: return False

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
    
    # Format: TITLE | asset.png | instructions | pause | text
    # Instructions can be empty now
    return f"{title} | {asset_name} | {asset_instr} | {pause} | {text}"
