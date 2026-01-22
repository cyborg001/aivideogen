import requests
import os
import random
import asyncio
import json
import re
import time
from django.conf import settings
# Lazy imports moved to function level for performance
from django.utils.text import slugify


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
    """Represents a visual asset (image/video) with effects"""
    def __init__(self, asset_type, zoom=None, move=None, overlay=None, fit=False):
        self.type = asset_type
        self.zoom = zoom  # "1.0:1.3"
        self.move = move  # "HOR:0:100"
        self.overlay = overlay  # "dust"
        self.fit = fit  # True = fit, False = cover


class AVGLSFX:
    """Represents a sound effect"""
    def __init__(self, sfx_type, volume=0.5, offset=0):
        self.type = sfx_type
        self.volume = volume
        self.offset = offset  # Word offset


class AVGLScene:
    """Represents a single scene in the video"""
    def __init__(self, title):
        self.title = title
        self.text = ""
        self.voice = None
        self.speed = None
        self.pitch = None # "+0Hz"
        self.assets = []  # List of AVGLAsset
        self.sfx = []  # List of AVGLSFX
        self.pause = 0.0
        self.subtitle = ""
        self.subtitles = [] # List of {"text": str, "offset": int, "duration": float}
        
        # Group Interpolation Internal Data
        self.group_id = None
        self.group_settings = None



class AVGLBlock:
    """Represents a logical block of scenes (e.g., Intro, Body, Outro)"""
    def __init__(self, title, music=None, volume=0.2):
        self.title = title
        self.scenes = []  # List of AVGLScene
        self.music = music  # Optional background music for this block
        self.volume = volume


class AVGLScript:
    """Represents the entire video script"""
    def __init__(self, title):
        self.title = title
        self.blocks = []  # List of AVGLBlock
        self.voice = "es-ES-AlvaroNeural"
        self.speed = "+0%"
        self.style = "neutral"
        self.background_music = None
        self.music_volume = 0.18

    def get_all_scenes(self):
        """Returns a flat list of all scenes in the script."""
        scenes = []
        for block in self.blocks:
            scenes.extend(block.scenes)
        return scenes


# ═══════════════════════════════════════════════════════════════════
# AVGL v4.0 - JSON Parser
# ═══════════════════════════════════════════════════════════════════

def parse_speed(val):
    """Converts speed value (float, int, or string like '+10%') to float factor (1.0 base)."""
    if val is None: return 1.0
    if isinstance(val, (int, float)): return float(val)
    
    s = str(val).strip()
    if s.endswith('%'):
        try:
            # Handle "+10%" -> 1.10, "-10%" -> 0.90
            pct = int(s.replace('%', ''))
            return 1.0 + (pct / 100.0)
        except:
            return 1.0
    return 1.0

def extract_subtitles_v35(text):
    """
    Extracts [SUB:] tags from text and calculates word offsets.
    Returns (clean_text, subtitles_list).
    """
    sub_pattern = r'\[SUB:\s*(.*?)\]'
    raw_subs = []
    
    # Iterate matches on original text
    all_matches = list(re.finditer(sub_pattern, text))
    
    for m in all_matches:
        content = m.group(1).strip()
        
        # Word Offset calculation (Clean version)
        text_before = text[:m.start()]
        clean_before = re.sub(r'\[.*?\]', '', text_before)
        word_idx = len(clean_before.split())
        
        # Parse: [SUB: word_count | text]
        word_count = None
        text_val = content
        if '|' in content:
            parts = [p.strip() for p in content.split('|')]
            try: 
                word_count = int(parts[0])
                text_val = parts[1] if len(parts) > 1 else ""
            except:
                try:
                    word_count = int(parts[1])
                    text_val = parts[0]
                except:
                    text_val = content
        
        raw_subs.append({
            "text": text_val,
            "offset": word_idx,
            "word_count": word_count,
            "duration": word_count # Alias for UI compatibility
        })
    
    # Sort subs by offset to ensure sequential rendering in video_engine
    raw_subs.sort(key=lambda x: x['offset'])
    
    # Final cleanup of the subtitle tags from the text
    clean_text = re.sub(sub_pattern, '', text).strip()
    
    return clean_text, raw_subs

def parse_avgl_json(json_text):
    """
    Parses AVGL v4.0 JSON format into AVGLScript object.
    Now supports Legacy 5-column text by auto-converting if JSON validation fails.
    """
    data = None
    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as e:
        if '|' in json_text:
             data = convert_text_to_avgl_json(json_text)
        else:
             raise ValueError(f"Formato desconocido (No es JSON ni Guion de Texto válido): {e.msg}")
    
    script = AVGLScript(title=data.get("title", "Video Sin Título"))
    
    # Robust parsing for voice/speed synonyms
    script.voice = data.get("voice") or data.get("voice_id") or "es-ES-AlvaroNeural"
    
    # Speed: handle numeric or string ("+10%")
    raw_speed = data.get("speed") or data.get("voice_speed")
    script.speed = parse_speed(raw_speed)
    
    script.style = data.get("style", "neutral")
    script.background_music = data.get("background_music")
    script.music_volume = data.get("music_volume", 0.18)
    
    blocks_data = data.get("blocks", [])
    if not blocks_data: pass # Tolerance

    for block_data in blocks_data:
        if not isinstance(block_data, dict): continue
        block = AVGLBlock(
            title=block_data.get("title", "Bloque Sin Título"),
            music=block_data.get("music"),
            volume=block_data.get("volume", 0.2)
        )
        
        scenes_data = block_data.get("scenes", [])
        if not isinstance(scenes_data, list): scenes_data = [scenes_data]

        # GROUP SUPPORT (Flattening)
        groups_data = block_data.get("groups", [])
        for group in groups_data:
            master_asset_data = group.get("master_asset")
            group_scenes = group.get("scenes", [])
            for s_data in group_scenes:
                # If scene has no assets, inherit master_asset from group
                # We copy to avoid mutating the original dict in unpredictable ways
                s_clone = s_data.get("scene", s_data).copy() if "scene" in s_data else s_data.copy()
                
                # Check if scene has VALID assets (not just empty list or empty dicts)
                has_valid_assets = False
                if s_clone.get("assets"):
                    for a in s_clone["assets"]:
                       if isinstance(a, dict) and (a.get("type") or a.get("id")):
                           # Check if value is not empty string
                           t = a.get("type") or a.get("id")
                           if t and str(t).strip() and str(t).strip().lower() != "image" and str(t).strip().lower() != "video":
                               has_valid_assets = True
                               break
                       elif isinstance(a, str) and a.strip():
                           has_valid_assets = True
                           break

                # Inherit Master Asset if needed
                if master_asset_data and not has_valid_assets:
                     s_clone["assets"] = [master_asset_data]
                
                # ATTACH GROUP METADATA (For Constant Velocity Interpolation)
                # We add underscore keys so AVGLScene constructor ignores them, 
                # but we will manually extract them later.
                s_clone["_group_id"] = f"g_{group.get('title', 'idx')}_{id(group)}"
                s_clone["_group_settings"] = {
                    "zoom": group.get("zoom"),
                    "move": group.get("move"),
                    "overlay": group.get("overlay"),
                    "fit": group.get("fit")
                }
                
                scenes_data.append(s_clone)
            
        for scene_data in scenes_data:
            if not isinstance(scene_data, dict): continue
            scene = AVGLScene(title=scene_data.get("title", "Escena Sin Título"))
            
            # Transfer group metadata for interpolation
            scene.group_id = scene_data.get("_group_id")
            scene.group_settings = scene_data.get("_group_settings")
            
            # Text
            raw_text = scene_data.get("text", "")
            if isinstance(raw_text, list): scene.text = " ".join([str(t) for t in raw_text if t])
            else: scene.text = str(raw_text)
                
            # Voice Fallback Logic
            s_voice = scene_data.get("voice")
            scene.voice = s_voice if s_voice else script.voice
            
            s_speed = scene_data.get("speed")
            # If scene speed is present, parse it. If not, use script speed (already parsed)
            scene.speed = parse_speed(s_speed) if s_speed is not None else script.speed
            
            scene.pitch = scene_data.get("pitch", None)
            scene.pause = scene_data.get("pause", 0.0)
            
            # SUBTITLES v3.5 (JSON Support)
            # If the editor saved tags in text, extract them
            clean_txt, extracted_subs = extract_subtitles_v35(scene.text)
            scene.text = clean_txt
            scene.subtitles = extracted_subs
            
            # If JSON already had a subtitles list, use it as fallback/merge
            json_subs = scene_data.get("subtitles", [])
            if json_subs and not scene.subtitles:
                scene.subtitles = json_subs
            
            scene.subtitle = scene_data.get("subtitle", "")
            
            # Assets ... (Skipping full detail for brevity in Replace, inferring context match)
            # Actually I should probably include assets parsing to be safe with context matching
            # logic, or rely on precise context.
            # I will just replace the Scene parsing part.
            
            # Parse assets
            assets_data = scene_data.get("assets", [])
            if isinstance(assets_data, (str, dict)): assets_data = [assets_data]
            for asset_data in assets_data:
                if isinstance(asset_data, str): asset = AVGLAsset(asset_type=asset_data)
                elif isinstance(asset_data, dict):
                    asset = AVGLAsset(
                        asset_type=asset_data.get("id") or asset_data.get("type"),
                        zoom=asset_data.get("zoom"),
                        move=asset_data.get("move"),
                        overlay=asset_data.get("overlay"),
                        fit=asset_data.get("fit", False)
                    )
                else: continue
                scene.assets.append(asset)
            
            # Parse SFX
            sfx_data = scene_data.get("sfx", [])
            if isinstance(sfx_data, (str, dict)): sfx_data = [sfx_data]
            for sfx_item in sfx_data:
                if isinstance(sfx_item, str):
                    scene.sfx.append(AVGLSFX(sfx_type=sfx_item))
                elif isinstance(sfx_item, dict):
                    sfx_type = sfx_item.get("type") or sfx_item.get("id")
                    if not sfx_type: continue # Skip if no type is found
                    
                    try:
                        vol = float(sfx_item.get("volume", 0.5))
                    except (ValueError, TypeError):
                        vol = 0.5
                        
                    try:
                        off = int(sfx_item.get("offset", 0))
                    except (ValueError, TypeError):
                        off = 0
                        
                    scene.sfx.append(AVGLSFX(
                        sfx_type=sfx_type,
                        volume=vol,
                        offset=off
                    ))
                else: continue
            
            block.scenes.append(scene)
        script.blocks.append(block)
    return script


def translate_emotions(text, use_ssml=False):
    """
    Translates custom emotion tags into SSML (legacy) or prepares for segmented mode.
    In the new v4.0 overhaul, we prefer segmented mode (use_ssml=False).
    """
    if not use_ssml:
        return text

    # Legacy SSML translation
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
        replacement = rf'<prosody {attr_str}>\1</prosody>'
        processed_text = re.sub(pattern, replacement, processed_text, flags=re.IGNORECASE | re.DOTALL)
    processed_text = re.sub(r'\[PAUSA:([\d\.]+)\]', r'<break time="\1s"/>', processed_text, flags=re.IGNORECASE)
    return processed_text


def wrap_ssml(text, voice, speed="+0%", pitch=None):
    """
    Wraps text in SSML tags if necessary.
    CRITICAL FIX: Use full SSML header to ensure Edge TTS correctly identifies it as markup.
    """
    if '<prosody' in text or '<break' in text or '<express-as' in text or (pitch and pitch != "+0Hz"):
        content = text
        
        # Apply Global Speed/Pitch Wrapper if not already wrapped
        # Note: If inner tags exist, this wraps AROUND them, which is valid SSML (prosody nesting).
        attrs = []
        if speed != "+0%": attrs.append(f'rate="{speed}"')
        if pitch and pitch != "+0Hz": attrs.append(f'pitch="{pitch}"')
        
        if attrs:
            attr_str = " ".join(attrs)
            content = f'<prosody {attr_str}>{text}</prosody>'
            
        # Robust header for Edge TTS
        return (
            f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
            f'xml:lang="es-ES"><voice name="{voice}">{content}</voice></speak>'
        )
    return text


# ═══════════════════════════════════════════════════════════════════
# Audio Generation (Edge TTS & ElevenLabs)
# ═══════════════════════════════════════════════════════════════════

async def generate_audio_edge(text, output_path, voice="es-ES-AlvaroNeural", rate="+0%", pitch="+0Hz"):
    """
    New Segmented Audio Engine (v4.0 Overhaul)
    Avoids SSML bloating by splitting text into blocks and joining them.
    """
    import edge_tts
    from moviepy import AudioFileClip, concatenate_audioclips, AudioClip
    import numpy as np

    emotions_config = {
        'TENSO': {'style': 'serious', 'rate': '-5%', 'pitch': '-3Hz'},
        'EPICO': {'style': 'excited', 'rate': '+10%', 'volume': '+15%', 'pitch': '+5Hz'},
        'SUSPENSO': {'style': 'whispering', 'rate': '-25%', 'pitch': '-2Hz'},
        'GRITANDO': {'style': 'shouting', 'rate': '+20%', 'volume': '+30%', 'pitch': '+15Hz'},
        'SUSURRO': {'style': 'whispering', 'rate': '-20%', 'volume': '-20%', 'pitch': '-5Hz'},
    }

    # 1. Parse Segments
    segments = []
    # Regex to find [TAG]text[/TAG] or [PAUSA:X.X] or plain text
    # We use a non-greedy approach for tags
    pattern = r'(\[PAUSA:[\d\.]+\]|\[([A-Z]+)\](.*?)\[/\2\])'
    
    last_end = 0
    for match in re.finditer(pattern, text, flags=re.IGNORECASE | re.DOTALL):
        # Plain text before the match
        if match.start() > last_end:
            plain = text[last_end:match.start()].strip()
            if plain:
                segments.append(('plain', plain))
        
        full_match = match.group(0)
        if full_match.upper().startswith('[PAUSA'):
            dur = float(re.search(r'[\d\.]+', full_match).group())
            segments.append(('pause', dur))
        else:
            tag = match.group(2).upper()
            content = match.group(3).strip()
            segments.append((tag, content))
        
        last_end = match.end()
    
    # Remaining text after last match
    if last_end < len(text):
        plain = text[last_end:].strip()
        if plain:
            segments.append(('plain', plain))

    if not segments:
        segments = [('plain', text)]

    # 2. Generate and store clips
    audio_clips = []
    voice_segments_metadata = [] # List of (start, end) relative to final clip
    
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_segments')
    os.makedirs(temp_dir, exist_ok=True)
    
    project_prefix = f"seg_{int(time.time())}_{random.randint(100,999)}"
    current_offset = 0.0

    try:
        for i, (tag, content) in enumerate(segments):
            if tag == 'pause':
                # Create silence clip
                silence = AudioClip(lambda t: np.zeros(2), duration=content).with_fps(44100)
                audio_clips.append(silence)
                current_offset += content
                continue
            
            # Text segment
            seg_path = os.path.join(temp_dir, f"{project_prefix}_{i}.mp3")
            
            # Determine segment voice (Switching support)
            seg_voice = voice
            if tag in VOICES_CONFIG:
                seg_voice = VOICES_CONFIG[tag]
            
            # Apply emotion settings
            seg_rate = rate
            seg_pitch = "+0Hz"
            seg_vol = "+0%"
            seg_style = "neutral"
            
            if tag in emotions_config:
                # Combine base rate with emotion rate numerically logic could be added here
                # For now we just override or keep simple
                seg_rate = emotions_config[tag].get('rate', rate)
                seg_vol = emotions_config[tag].get('volume', '+0%')
                seg_pitch = emotions_config[tag].get('pitch', "+0Hz")
                seg_style = emotions_config[tag].get('style', "neutral")
            
            # Edge TTS call with Native Style (SSML)
            # We must construct a valid SSML string if we want to use express-as
            # or if we have specific pitch requirements that Communicate() args don't cover well.
            # However, edge_tts.Communicate() handles rate/volume/pitch args nicely.
            # Only style needs SSML wrapping usually.
            
            # Construct SSML for style if not neutral
            if seg_style != "neutral":
                 # We need to wrap it ourselves because edge_tts doesn't have a 'style' arg in init
                 # But getting the full SSML right with Communicate(ssml_content) is tricky.
                 # Strategy: Wrap content in <express-as> and let Communicate handle the rest?
                 # Communicate(text) -> raw text. Communicate(ssml) -> raw ssml.
                 
                 ssml_content = f'<express-as style="{seg_style}">{content}</express-as>'
                 # We must wrap this in speak/voice tags too if we pass it as SSML
                 full_ssml = wrap_ssml(ssml_content, seg_voice, speed=seg_rate)
                 # Note: wrap_ssml handles rate via prosody, but pitch is missing there properly.
                 # Let's update wrap_ssml later or hack it here.
                 # For now, let's rely on updated wrap_ssml which we should also fix if needed,
                 # but here is the direct implementation:
                 
                 prosody_attrs = f'rate="{seg_rate}" volume="{seg_vol}" pitch="{seg_pitch}"'
                 final_ssml = (
                    f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="es-ES">'
                    f'<voice name="{seg_voice}">'
                    f'<express-as style="{seg_style}">'
                    f'<prosody {prosody_attrs}>'
                    f'{content}'
                    f'</prosody>'
                    f'</express-as>'
                    f'</voice>'
                    f'</speak>'
                 )
                 communicate = edge_tts.Communicate(final_ssml, seg_voice) # voice arg is redundant if in ssml but harmless
            else:
                 # Standard clean call
                 communicate = edge_tts.Communicate(content, seg_voice, rate=seg_rate, volume=seg_vol, pitch=seg_pitch)

            await communicate.save(seg_path)
            
            # Clean technical tags/XML and instructions in parentheses (Soportamos acotaciones)
            clean_content = re.sub(r'<[^>]+>', '', content) # Strip XML
            clean_content = re.sub(r'\(.*?\)', '', clean_content) # Strip (...)
            
            # Translate Cinematic Actions (TOS, AJEM, etc.)
            for action_tag, onomatopoeia in ACTIONS_CONFIG.items():
                clean_content = clean_content.replace(action_tag, onomatopoeia)
            
            clean_content = clean_content.strip()
            if not clean_content: continue

            # Determine segment voice (Switching support)
            seg_voice = voice
            if tag in VOICES_CONFIG:
                seg_voice = VOICES_CONFIG[tag]

            # Edge TTS call
            communicate = edge_tts.Communicate(clean_content, seg_voice, rate=seg_rate, volume=seg_vol, pitch=seg_pitch)
            await communicate.save(seg_path)
            
            if os.path.exists(seg_path):
                clip = AudioFileClip(seg_path)
                
                # Track interval
                voice_segments_metadata.append((current_offset, current_offset + clip.duration))
                
                audio_clips.append(clip)
                current_offset += clip.duration

        # 3. Join Clips
        if audio_clips:
            final_audio = concatenate_audioclips(audio_clips)
            final_audio.write_audiofile(output_path, logger=None)
            
            # Cleanup
            for clip in audio_clips:
                clip.close()
            
            return (True, voice_segments_metadata)
        return (False, [])
        
    except Exception as e:
        print(f"❌ Error en segmentación de audio: {e}")
        return (False, [])


async def generate_audio_elevenlabs(text, output_path, voice_id, api_key):
    # 0. Clean SSML/XML tags to prevent "reading the tags"
    clean_text = re.sub(r'<[^>]+>', '', text).strip()
    if not clean_text: return False
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    from elevenlabs.client import ElevenLabs
    from elevenlabs import save
    try:
        # ElevenLabs doesn't understand SSML, so strip all XML tags
        clean_text = re.sub(r'<[^>]+>', '', text)
        clean_text = re.sub(r'\[.*?\]', '', clean_text).strip()
        
        client = ElevenLabs(api_key=api_key)
        audio_gen = client.text_to_speech.convert(
            text=clean_text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2"
        )
        save(audio_gen, output_path)
        return True
    except Exception as e:
        print(f"Error in generate_audio_elevenlabs: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════
# Text-to-JSON Converter (Unified Engine Bridge)
# ═══════════════════════════════════════════════════════════════════

def convert_text_to_avgl_json(text_script, title="Nuevo Video"):
    """
    Converts legacy 5-column text script into AVGL v4 JSON structure.
    Enables FIT, ZOOM and OVERLAY support for text-mode scripts.
    
    Format: TITULO | ASSET | DIRECTION/EFFECT | TEXT | PAUSE
    """
    script = {
        "title": title,
        "voice": "es-ES-AlvaroNeural",
        "speed": 1.0,
        "style": "neutral",
        "blocks": []
    }
    
    # Single block for text-converted scripts
    block = {
        "title": "Capítulo Principal",
        "scenes": []
    }
    
    lines = text_script.strip().split('\n')
    
    for line in lines:
        if not line.strip() or line.strip().startswith('#'):
            continue
            
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 3:
            continue
            
        # Parse fields
        s_title = parts[0]
        s_asset = parts[1]
        
        # Direction/Effect logic
        s_dir = ""
        s_text = ""
        s_pause = 0.0
        
        # Smart detection of columns based on content
        # Legacy 3-col: TITLE | ASSET | TEXT
        # Legacy 4-col: TITLE | ASSET | DIR | TEXT
        # Pro 5-col:    TITLE | ASSET | DIR | TEXT | PAUSE
        
        if len(parts) == 3:
            # Ambiguity: Is p[2] text or direction? 
            # Legacy engine assumed Text. We stick to that.
            s_text = parts[2]
            
        elif len(parts) >= 4:
            s_dir = parts[2] # "FIT + ZOOM..."
            s_text = parts[3]
            
            if len(parts) >= 5:
                try: s_pause = float(parts[4])
                except: s_pause = 0.0

        # 1. Extract SFX from Text
        # Syntax: [SFX: name | vol | offset]
        sfx_pattern = r'\[SFX:\s*(.*?)\]'
        sfx_matches = list(re.finditer(sfx_pattern, s_text, flags=re.IGNORECASE))
        scene_sfx = []
        for m in sfx_matches:
            content = m.group(1).strip()
            parts_sfx = [p.strip() for p in content.split('|')]
            name = parts_sfx[0]
            vol = 0.5
            off = 0
            if len(parts_sfx) > 1:
                try: vol = float(parts_sfx[1])
                except: pass
            if len(parts_sfx) > 2:
                try: off = int(parts_sfx[2])
                except: pass
            scene_sfx.append({"type": name, "volume": vol, "offset": off})
        
        # Remove SFX tags from text
        s_text = re.sub(sfx_pattern, '', s_text, flags=re.IGNORECASE)

        # 2. Extract OVERLAY from Text
        # Syntax: [OVERLAY: name]
        ov_pattern = r'\[OVERLAY:\s*(.*?)\]'
        ov_matches = list(re.finditer(ov_pattern, s_text, flags=re.IGNORECASE))
        text_overlay = None
        if ov_matches:
            text_overlay = ov_matches[0].group(1).strip()
        
        # Remove Overlay tags from text
        s_text = re.sub(ov_pattern, '', s_text, flags=re.IGNORECASE)

        # 3. Subtitle Extraction v3.5 (Using Refactored Logic)
        s_text, raw_subs = extract_subtitles_v35(s_text)
        
        # 4. Final cleanup for the database (remove any remaining emotion/speaker tags for clean storage if needed)
        # However, we WANT to keep [EMOTION] tags for the runner. 
        # But we remove speaker tags like [NARRADOR] or [ETHAN] for cleaner subtitles/logs if they are at the very start.
        s_text_clean = re.sub(r'^\[[^\]]+\]\s*', '', s_text).strip()
        
        # Process Direction/Effect into Asset Params
        # Syntax: "FIT + ZOOM:1.0:1.3 + OVERLAY:dust"
        asset_obj = {
            "id": s_asset,
            "type": "video" if s_asset.lower().endswith(('.mp4', '.mov', '.avi')) else "image",
            "fit": False
        }
        
        if text_overlay:
            asset_obj['overlay'] = text_overlay

        if 'FIT' in s_dir.upper():
            asset_obj['fit'] = True
            
        # Split by '+'
        dir_parts = [d.strip() for d in s_dir.split('+')]
        
        for part in dir_parts:
            up = part.upper()
            if 'ZOOM' in up:
                if ':' in part: asset_obj['zoom'] = part.split(':', 1)[1]
            if up.startswith('HOR') or up.startswith('VER'):
                asset_obj['move'] = part
            if 'OVERLAY' in up:
                subparts = part.split(':')
                if len(subparts) > 1:
                    asset_obj['overlay'] = subparts[1]
        
        scene = {
            "title": s_title,
            "text": s_text,
            "assets": [asset_obj],
            "sfx": scene_sfx,
            "pause": s_pause,
            "subtitles": raw_subs
        }
        block['scenes'].append(scene)
        
    script['blocks'].append(block)
    return script


def convert_avgl_json_to_text(script_json):
    """
    Converts AVGL v4.0 JSON back to legacy-style 5-column text,
    but preserving metadata as [TAGS] inside the text column.
    """
    lines = []
    
    # Global Header (Optional but good for completeness)
    # lines.append(f"VOICE: {script_json.get('voice', 'es-ES-AlvaroNeural')}")
    # lines.append(f"MUSIC: {script_json.get('background_music', 'None')}")
    
    blocks = script_json.get('blocks', [])
    for b in blocks:
        lines.append(f"--- {b.get('title', 'Bloque')} ---")
        
        scenes = b.get('scenes', [])
        for s in scenes:
            title = s.get('title', 'Scene')
            
            # Asset Logic
            asset = s.get('assets', [{}])[0]
            asset_path = asset.get('id') or asset.get('type') or "empty"
            
            # Directives
            dir_parts = []
            if asset.get('fit'): dir_parts.append("FIT")
            if asset.get('zoom'): dir_parts.append(f"ZOOM:{asset['zoom']}")
            if asset.get('move'): dir_parts.append(asset['move'])
            if asset.get('overlay'): dir_parts.append(f"OVERLAY:{asset['overlay']}")
            
            directives = " + ".join(dir_parts) if dir_parts else "NORMAL"
            
            # Text with embedded metadata
            text = s.get('text', '')
            
            # Re-inject Subtitles
            subs = s.get('subtitles', [])
            # For simplicity, we only re-inject if text doesn't already have them? 
            # Actually, convert_avgl_json_to_text is usually called on data that ALREADY had them stripped.
            if subs:
                # We sort subs by offset and inject them (approximate)
                words = text.split()
                # Sort in reverse to not mess up offsets during injection
                sorted_subs = sorted(subs, key=lambda x: x.get('offset', 0), reverse=True)
                for sub in sorted_subs:
                    off = sub.get('offset', 0)
                    t_val = sub.get('text', '')
                    w_count = sub.get('word_count') or sub.get('duration') or 3
                    tag = f" [SUB: {w_count} | {t_val}] "
                    if off >= len(words):
                        words.append(tag)
                    else:
                        words.insert(off, tag)
                text = " ".join(words)

            # Re-inject SFX
            sfx_list = s.get('sfx', [])
            for sfx in sfx_list:
                s_type = sfx.get('type') or sfx.get('id')
                s_vol = sfx.get('volume', 0.5)
                s_off = sfx.get('offset', 0)
                text += f" [SFX: {s_type} | {s_vol} | {s_off}]"
            
            # Re-inject Overlay if not in directives (as fallback/alternative)
            # Actually we already put it in directives.

            pause = s.get('pause', 0.5)
            
            # Format: TITLE | ASSET | DIR | TEXT | PAUSE
            line = f"{title} | {asset_path} | {directives} | {text} | {pause}"
            lines.append(line)
            
        lines.append("") # Empty line between blocks
        
    return "\n".join(lines)


