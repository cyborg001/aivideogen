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
    Extracts subtitles from tags. Preserves the text for the narrator.
    v6.8: Robust Mapping Logic. Eliminates repetition and silence bugs.
    """
    # 1. Identify all tags and their contents
    # This regex catches: [SUB]content[/SUB] OR [SUB: content]
    # We use a combined pattern to ensure we don't miss anything.
    wrapped_pattern = re.compile(r'\[\s*SUB\s*\](.*?)\s*\[\s*/SUB\s*\]', re.IGNORECASE | re.DOTALL)
    simple_pattern = re.compile(r'\[\s*SUB\s*:\s*(.*?)\s*\]', re.IGNORECASE)
    
    tags = []
    
    # Process wrapped tags first
    for m in wrapped_pattern.finditer(text):
        tags.append({'start': m.start(), 'end': m.end(), 'content': m.group(1).strip(), 'type': 'wrapped'})
    
    # Process simple tags, but only if they don't overlap with a wrapped tag
    for m in simple_pattern.finditer(text):
        if not any(t['start'] <= m.start() < t['end'] for t in tags):
            tags.append({'start': m.start(), 'end': m.end(), 'content': m.group(1).strip(), 'type': 'simple'})
            
    # Sort tags by appearance
    tags.sort(key=lambda x: x['start'])
    
    # 2. Build clean text and track word positions
    clean_parts = []
    last_idx = 0
    raw_subs = []
    
    current_clean_text = ""
    
    for tag in tags:
        # Text before tag
        before = text[last_idx:tag['start']]
        current_clean_text += before
        
        # Word index in current clean text
        word_offset = len(current_clean_text.split())
        
        # Tag content
        content = tag['content']
        display_text = content
        word_count = 3
        
        if tag['type'] == 'simple' and '|' in content:
            parts = [p.strip() for p in content.split('|')]
            try:
                word_count = int(parts[0])
                display_text = parts[1] if len(parts) > 1 else ""
            except:
                display_text = parts[0]
        else:
            word_count = len(display_text.split())
            if word_count < 2: word_count = 3
            
        raw_subs.append({"text": display_text, "offset": word_offset, "word_count": word_count})
        
        # Add content to narration
        current_clean_text += display_text
        last_idx = tag['end']
        
    # Final piece
    current_clean_text += text[last_idx:]
    
    # One last safety: strip any stray brackets that weren't caught
    clean_text = re.sub(r'\[\s*/?SUB\s*(?::.*?)?\]', '', current_clean_text, flags=re.IGNORECASE)
    
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
    script.music_volume = data.get("music_volume", 0.18)
    # v7.5 Metadata
    script.fuentes = data.get("fuentes", "")
    script.tags = data.get("tags", "")
    script.hashtags = data.get("hashtags", "")
    
    for block_data in data.get("blocks", []):
        block = AVGLBlock(
            title=block_data.get("title", "Bloque"), 
            music=block_data.get("music"), 
            volume=block_data.get("volume", 0.2)
        )
        # Block-level Voice Overrides
        block.voice = block_data.get("voice")
        block.voice_speed = parse_speed(block_data.get("voice_speed")) if block_data.get("voice_speed") else None
        
        # Flatten Groups
        scenes_to_process = block_data.get("scenes", []).copy()
        for group in block_data.get("groups", []):
            master_asset = group.get("master_asset")
            for s_data in group.get("scenes", []):
                s_clone = s_data.copy()
                if master_asset and not s_clone.get("assets"):
                    s_clone["assets"] = [master_asset]
                s_clone["_group_id"] = f"g_{id(group)}"
                s_clone["_group_settings"] = group
                scenes_to_process.append(s_clone)
        
        for s_data in scenes_to_process:
            scene = AVGLScene(title=s_data.get("title", "Escena"))
            scene.group_id = s_data.get("_group_id")
            scene.group_settings = s_data.get("_group_settings")
            scene.text = str(s_data.get("text", ""))
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
    current_block = {"title": "Capítulo Principal", "scenes": []}
    for line in lines:
        raw_line = line.strip()
        if not raw_line: continue
        
        # v7.5: Metadata extraction from comments
        if raw_line.startswith('#'):
            low_line = raw_line.lower()
            if 'fuentes:' in low_line: script["fuentes"] = raw_line.split(':', 1)[1].strip()
            elif 'tags:' in low_line: script["tags"] = raw_line.split(':', 1)[1].strip()
            elif 'hashtags:' in low_line: script["hashtags"] = raw_line.split(':', 1)[1].strip()
            continue
            
        if raw_line.startswith('---'):
            if current_block["scenes"]: script["blocks"].append(current_block)
            current_block = {"title": raw_line.replace('-', '').strip(), "scenes": []}
            continue

        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 3:
            scene = {"title": parts[0], "text": parts[-1], "assets": [{"id": parts[1]}]}
            if len(parts) >= 4:
                dir_str = parts[2].upper()
                if 'ZOOM' in dir_str:
                    z = re.search(r'ZOOM:([\d\.]+):([\d\.]+)', dir_str)
                    if z: scene["assets"][0]["zoom"] = f"{z.group(1)}:{z.group(2)}"
                if 'FIT' in dir_str: scene["assets"][0]["fit"] = True
            if len(parts) >= 5:
                try: scene["pause"] = float(parts[4])
                except: pass
            current_block["scenes"].append(scene)
            
    if current_block["scenes"]: script["blocks"].append(current_block)
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
        
        for scene in block.get("scenes", []):
            title = scene.get("title", "Escena")
            text = scene.get("text", "")
            
            # Asset logic
            asset_name = "negro.png"
            asset_instr = "."
            if scene.get("assets") and len(scene["assets"]) > 0:
                asset = scene["assets"][0]
                asset_name = asset.get("id") or asset.get("type") or "negro.png"
                
                # Instructions (Zoom/Fit)
                instr_parts = []
                if asset.get("zoom"): instr_parts.append(f"ZOOM:{asset['zoom']}")
                if asset.get("fit"): instr_parts.append("FIT")
                if asset.get("move"): instr_parts.append(f"MOVE:{asset['move']}")
                
                if instr_parts:
                    asset_instr = " ".join(instr_parts)
            
            pause = scene.get("pause", 0.0)
            
            # Format: TITLE | asset.png | instructions | pause | text
            lines.append(f"{title} | {asset_name} | {asset_instr} | {pause} | {text}")
        
        lines.append("") # Spacer between blocks
        
    return "\n".join(lines).strip()
