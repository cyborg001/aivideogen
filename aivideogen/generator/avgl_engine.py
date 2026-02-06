import os
import random
import asyncio
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
    'ETHAN': 'es-US-AlonsoNeural',
    'CHARLI': 'es-DO-EmilioNeural',
    'CARLOS': 'es-DO-EmilioNeural',
    'SONY': 'es-MX-DaliaNeural',
    'NARRADOR': 'es-MX-JorgeNeural',
    'CIENTIFICO': 'es-MX-JorgeNeural',
    'JOVEN': 'es-US-AlonsoNeural'
}

ACTIONS_CONFIG = {
    '[TOS]': 'cof, cof...',
    '[AJEM]': 'ajem...',
    '[SUSPIRO]': 'uf...',
    '[SORPRESA]': '¡oh!',
    '[RISA]': 'ja, ja, ja...'
}

class AVGLAsset:
    def __init__(self, asset_type, zoom=None, move=None, overlay=None, fit=False):
        self.type = asset_type
        self.zoom = zoom
        self.move = move
        self.overlay = overlay
        self.fit = fit

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
        self.voice = "es-ES-AlvaroNeural"
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

def extract_subtitles_v35(text):
    """
    Extracts subtitles and narration from tags. 
    Supports:
    - [SUB]text[/SUB] -> Narration and Subtitle are the same.
    - [SUB: count | text] -> Subtitle with specific word count duration.
    - [PHO]narration | subtitle[/PHO] -> Narrator says one thing, subtitle shows another.
    v8.7: Enhanced with [PHO] to handle phonetic overrides like "IAs".
    """
    import re
    
    # 1. Identify all tags
    patterns = {
        'wrapped': re.compile(r'\[\s*SUB\s*\](.*?)\s*\[\s*/SUB\s*\]', re.IGNORECASE | re.DOTALL),
        'simple': re.compile(r'\[\s*SUB\s*:\s*(.*?)\s*\]', re.IGNORECASE),
        'pho': re.compile(r'\[\s*PHO\s*\](.*?)\s*\[\s*/PHO\s*\]', re.IGNORECASE | re.DOTALL)
    }
    
    all_tags = []
    for t_type, pattern in patterns.items():
        for m in pattern.finditer(text):
            all_tags.append({
                'start': m.start(),
                'end': m.end(),
                'content': m.group(1).strip(),
                'type': t_type
            })
            
    # Sort and remove overlaps (first one wins)
    all_tags.sort(key=lambda x: x['start'])
    tags = []
    last_end = 0
    for t in all_tags:
        if t['start'] >= last_end:
            tags.append(t)
            last_end = t['end']
            
    # 2. Build clean text and subtitles
    current_clean_text = ""
    last_idx = 0
    raw_subs = []
    
    for tag in tags:
        # Text before tag
        before = text[last_idx:tag['start']]
        current_clean_text += before
        
        # Word index in current clean text
        word_offset = len(current_clean_text.split())
        
        content = tag['content']
        display_text = ""
        narrator_text = ""
        word_count = 3
        
        if tag['type'] == 'pho':
            # Format: narration | subtitle
            if '|' in content:
                parts = [p.strip() for p in content.split('|')]
                narrator_text = parts[0]
                display_text = parts[1] if len(parts) > 1 else parts[0]
            else:
                narrator_text = content
                display_text = content
            word_count = len(narrator_text.split())
            if word_count < 2: word_count = 3
            
        elif tag['type'] == 'simple' and '|' in content:
            # Format: count | subtitle
            parts = [p.strip() for p in content.split('|')]
            try:
                word_count = int(parts[0])
                display_text = parts[1] if len(parts) > 1 else ""
            except:
                display_text = parts[0]
            narrator_text = display_text # Simple SUB usually repeats
            
        else:
            # Standard [SUB] or [SUB:...]
            display_text = content
            narrator_text = content
            word_count = len(display_text.split())
            if word_count < 2: word_count = 3
            
        raw_subs.append({"text": display_text, "offset": word_offset, "word_count": word_count})
        
        # Add content to narration
        current_clean_text += narrator_text
        last_idx = tag['end']
        
    # Final piece
    current_clean_text += text[last_idx:]
    
    # Strip any stray brackets (safety)
    clean_text = re.sub(r'\[\s*/?SUB\s*(?::.*?)?\]', '', current_clean_text, flags=re.IGNORECASE)
    clean_text = re.sub(r'\[\s*/?PHO\s*\]', '', clean_text, flags=re.IGNORECASE)
    
    return clean_text.strip(), raw_subs

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
        block = AVGLBlock(
            title=block_data.get("title", "Bloque"), 
            music=block_data.get("music"), 
            volume=block_data.get("volume", 0.2)
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
            
            clean_txt, extracted_subs = extract_subtitles_v35(scene.text)
            scene.text = clean_txt
            scene.subtitles = extracted_subs or s_data.get("subtitles", [])
            
            for a_data in s_data.get("assets", []):
                if isinstance(a_data, str): scene.assets.append(AVGLAsset(a_data))
                else: scene.assets.append(AVGLAsset(a_data.get("id") or a_data.get("type"), a_data.get("zoom"), a_data.get("move"), a_data.get("overlay"), a_data.get("fit", False)))
            
            for sfx_data in s_data.get("sfx", []):
                if isinstance(sfx_data, str): scene.sfx.append(AVGLSFX(sfx_data))
                else: scene.sfx.append(AVGLSFX(sfx_data.get("type") or sfx_data.get("id"), sfx_data.get("volume", 0.5), sfx_data.get("offset", 0)))
            
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

                # Inheritance from Group Master Asset
                assets_to_use = s_data.get("assets", [])
                if not assets_to_use and master_asset:
                    assets_to_use = [master_asset]
                
                for a_data in assets_to_use:
                    if isinstance(a_data, str): scene.assets.append(AVGLAsset(a_data))
                    else: scene.assets.append(AVGLAsset(a_data.get("id") or a_data.get("type"), a_data.get("zoom"), a_data.get("move"), a_data.get("overlay"), a_data.get("fit", False)))

                for sfx_data in s_data.get("sfx", []):
                    if isinstance(sfx_data, str): scene.sfx.append(AVGLSFX(sfx_data))
                    else: scene.sfx.append(AVGLSFX(sfx_data.get("type") or sfx_data.get("id"), sfx_data.get("volume", 0.5), sfx_data.get("offset", 0)))
                
                block.scenes.append(scene)

        script.blocks.append(block)
    return script

def translate_emotions(text, use_ssml=False):
    if not use_ssml: return text
    import xml.sax.saxutils as saxutils
    emotions = {
        'TENSO': {'pitch': '-10Hz', 'rate': '-15%'},
        'EPICO': {'pitch': '+5Hz', 'rate': '+10%', 'volume': '+15%'},
        'SUSPENSO': {'pitch': '-5Hz', 'rate': '-25%'},
        'GRITANDO': {'pitch': '+15Hz', 'rate': '+20%', 'volume': 'loud'},
        'SUSURRO': {'pitch': '-12Hz', 'rate': '-20%', 'volume': '-30%'},
    }
    processed_text = saxutils.escape(text)
    for tag, attrs in emotions.items():
        pattern = rf'\[{tag}\](.*?)\[/{tag}\]'
        attr_str = " ".join([f'{k}="{v}"' for k, v in attrs.items()])
        processed_text = re.sub(pattern, rf'<prosody {attr_str}>\1</prosody>', processed_text, flags=re.IGNORECASE | re.DOTALL)
    processed_text = re.sub(r'\[PAUSA:([\d\.]+)\]', r'<break time="\1s"/>', processed_text, flags=re.IGNORECASE)
    return processed_text

def wrap_ssml(text, voice, speed="+0%", pitch=None):
    if '<prosody' in text or '<break' in text:
        content = text
        attrs = []
        if speed != "+0%": attrs.append(f'rate="{speed}"')
        if pitch and pitch != "+0Hz": attrs.append(f'pitch="{pitch}"')
        if attrs: content = f'<prosody {" ".join(attrs)}>{text}</prosody>'
        return f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="es-ES"><voice name="{voice}">{content}</voice></speak>'
    return text

# ═══════════════════════════════════════════════════════════════════
# Audio Generation (Edge TTS & ElevenLabs)
# ═══════════════════════════════════════════════════════════════════

async def generate_audio_edge(text, output_path, voice="es-ES-AlvaroNeural", rate="+0%", pitch="+0Hz", scene=None):
    """
    Robust Segmented Engine (v6.5)
    Splits by [PAUSA:X.X], strips all other tags, and joins audio files.
    Tracks voice_intervals if scene object is provided.
    """
    import edge_tts
    pause_pattern = r'\[PAUSA:([\d\.]+)\]'
    parts = re.split(pause_pattern, text, flags=re.IGNORECASE)
    segments = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            try: segments.append(('pause', float(part)))
            except: pass
        else:
            clean = re.sub(r'\[.*?\]', '', part)
            clean = re.sub(r'\(.*?\)', '', clean)
            clean = re.sub(r'<.*?>', '', clean)
            clean = re.sub(r'(?i)\b(SPEED|ZOOM|AUDIO|SFX|FIT|MOVE|PAN|VOICE|PITCH|TITLE|INSTRUCCIÓN|INSTRUCTION)\s*:.*', '', clean)
            clean = clean.strip()
            if clean: segments.append(('text', clean))
    if not segments: return False
    audio_clips = []
    temp_files = []
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_segments')
    os.makedirs(temp_dir, exist_ok=True)
    prefix = f"seg_{int(time.time())}_{random.randint(100,999)}"
    current_time = 0.0
    voice_intervals = []
    
    try:
        for i, (tag, val) in enumerate(segments):
            if tag == 'pause':
                silence = AudioClip(lambda t: np.zeros(2), duration=val).with_fps(44100)
                audio_clips.append(silence)
                current_time += val
            else:
                seg_path = os.path.join(temp_dir, f"{prefix}_{i}.mp3")
                temp_files.append(seg_path)
                communicate = edge_tts.Communicate(val, voice, rate=rate, pitch=pitch)
                await communicate.save(seg_path)
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
    asset_name = "negro.png"
    asset_instr = "" # Default empty (v9.8 Fix: No more dots)
    
    # Support both 'assets' (list) and 'asset' (single string/object)
    assets_list = scene.get("assets")
    if not assets_list and scene.get("asset"):
        assets_list = [scene.get("asset")]
        
    if assets_list and len(assets_list) > 0:
        asset = assets_list[0]
        if isinstance(asset, str):
            asset_name = asset
        else:
            asset_name = asset.get("id") or asset.get("type") or "negro.png"
        
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
