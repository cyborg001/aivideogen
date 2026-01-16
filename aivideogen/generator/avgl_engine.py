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
# AVGL v4.0 - Data Classes (JSON-based)
# ═══════════════════════════════════════════════════════════════════

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
        self.assets = []  # List of AVGLAsset
        self.sfx = []  # List of AVGLSFX
        self.pause = 0.0


class AVGLBlock:
    """Represents a chapter/block in the video"""
    def __init__(self, title, music=None, volume=0.2):
        self.title = title
        self.music = music
        self.volume = volume
        self.scenes = []  # List of AVGLScene


class AVGLScript:
    """Represents the complete video script"""
    def __init__(self, title="Video Sin Título"):
        self.title = title
        self.voice = "es-ES-AlvaroNeural"
        self.speed = 1.0
        self.style = "neutral"
        self.background_music = None
        self.music_volume = 0.18
        self.blocks = []  # List of AVGLBlock
    
    def get_all_scenes(self):
        """Returns a flat list of all scenes"""
        scenes = []
        for block in self.blocks:
            scenes.extend(block.scenes)
        return scenes


# ═══════════════════════════════════════════════════════════════════
# AVGL v4.0 - JSON Parser
# ═══════════════════════════════════════════════════════════════════

def parse_avgl_json(json_text):
    """
    Parses AVGL v4.0 JSON format into AVGLScript object.
    Raises ValueError if JSON is invalid.
    """
    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON inválido en línea {e.lineno}: {e.msg}")
    
    # Create script with metadata
    script = AVGLScript(title=data.get("title", "Video Sin Título"))
    script.voice = data.get("voice", "es-ES-AlvaroNeural")
    script.speed = data.get("speed", 1.0)
    script.style = data.get("style", "neutral")
    script.background_music = data.get("background_music")
    script.music_volume = data.get("music_volume", 0.18)
    
    # Parse blocks
    blocks_data = data.get("blocks", [])
    if not blocks_data:
        raise ValueError("El script debe tener al menos un 'block'")
    
    for block_data in blocks_data:
        if not isinstance(block_data, dict):
            continue
            
        block = AVGLBlock(
            title=block_data.get("title", "Bloque Sin Título"),
            music=block_data.get("music"),
            volume=block_data.get("volume", 0.2)
        )
        
        # Parse scenes
        scenes_data = block_data.get("scenes", [])
        if not isinstance(scenes_data, list):
            scenes_data = [scenes_data] # Tolerance
            
        for scene_data in scenes_data:
            if not isinstance(scene_data, dict):
                continue
                
            scene = AVGLScene(title=scene_data.get("title", "Escena Sin Título"))
            
            # Support multiple texts (list) or single text (string)
            raw_text = scene_data.get("text", "")
            if isinstance(raw_text, list):
                scene.text = " ".join([str(t) for t in raw_text if t])
            else:
                scene.text = str(raw_text)
                
            scene.voice = scene_data.get("voice", script.voice)
            scene.speed = scene_data.get("speed", script.speed)
            scene.pause = scene_data.get("pause", 0.0)
            
            # Parse assets
            assets_data = scene_data.get("assets", [])
            # Support single asset provided as string or dict
            if isinstance(assets_data, (str, dict)):
                assets_data = [assets_data]
            
            for asset_data in assets_data:
                if isinstance(asset_data, str):
                    asset = AVGLAsset(asset_type=asset_data)
                elif isinstance(asset_data, dict):
                    # Support both 'type' and 'id'
                    asset_type = asset_data.get("type") or asset_data.get("id")
                    asset = AVGLAsset(
                        asset_type=asset_type,
                        zoom=asset_data.get("zoom"),
                        move=asset_data.get("move"),
                        overlay=asset_data.get("overlay"),
                        fit=asset_data.get("fit", False)
                    )
                else:
                    continue
                scene.assets.append(asset)
            
            # Parse SFX
            sfx_data = scene_data.get("sfx", [])
            # Support single SFX as string or dict
            if isinstance(sfx_data, (str, dict)):
                sfx_data = [sfx_data]
                
            for sfx_item in sfx_data:
                if isinstance(sfx_item, str):
                    sfx = AVGLSFX(sfx_type=sfx_item)
                elif isinstance(sfx_item, dict):
                    # Support both 'type' and 'id'
                    sfx_type = sfx_item.get("type") or sfx_item.get("id")
                    sfx = AVGLSFX(
                        sfx_type=sfx_type,
                        volume=sfx_item.get("volume", 0.5),
                        offset=sfx_item.get("offset", 0)
                    )
                else:
                    continue
                scene.sfx.append(sfx)
            
            block.scenes.append(scene)
        
        script.blocks.append(block)
    
    return script


# ═══════════════════════════════════════════════════════════════════
# Emotion Translator (SSML for Edge TTS)
# ═══════════════════════════════════════════════════════════════════

def translate_emotions(text, use_ssml=False):
    """
    Translates custom emotion tags into SSML (legacy) or prepares for segmented mode.
    In the new v4.0 overhaul, we prefer segmented mode (use_ssml=False).
    """
    if not use_ssml:
        # We don't strip here because generate_audio_edge will use the tags to split
        return text

    # Legacy SSML translation (kept for fallback)
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


def wrap_ssml(text, voice, speed="+0%"):
    """
    Wraps text in SSML tags if necessary.
    CRITICAL FIX: Use full SSML header to ensure Edge TTS correctly identifies it as markup.
    """
    if '<prosody' in text or '<break' in text:
        content = text
        if speed != "+0%":
            content = f'<prosody rate="{speed}">{text}</prosody>'
            
        # Robust header for Edge TTS
        return (
            f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
            f'xml:lang="es-ES"><voice name="{voice}">{content}</voice></speak>'
        )
    return text


# ═══════════════════════════════════════════════════════════════════
# Audio Generation (Edge TTS & ElevenLabs)
# ═══════════════════════════════════════════════════════════════════

async def generate_audio_edge(text, output_path, voice="es-ES-AlvaroNeural", rate="+0%"):
    """
    New Segmented Audio Engine (v4.0 Overhaul)
    Avoids SSML bloating by splitting text into blocks and joining them.
    """
    import edge_tts
    from moviepy import AudioFileClip, concatenate_audioclips, AudioClip
    import numpy as np

    emotions_config = {
        'TENSO': {'rate': '-15%', 'volume': '+0%'},
        'EPICO': {'rate': '+10%', 'volume': '+15%'},
        'SUSPENSO': {'rate': '-25%', 'volume': '+0%'},
        'GRITANDO': {'rate': '+20%', 'volume': '+30%'},
        'SUSURRO': {'rate': '-20%', 'volume': '-30%'},
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
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_segments')
    os.makedirs(temp_dir, exist_ok=True)
    
    project_prefix = f"seg_{int(time.time())}_{random.randint(100,999)}"

    try:
        for i, (tag, content) in enumerate(segments):
            if tag == 'pause':
                # Create silence clip
                # Fix: Use np.zeros(2) for stereo and set fps to match typical audio
                silence = AudioClip(lambda t: np.zeros(2), duration=content).with_fps(44100)
                audio_clips.append(silence)
                continue
            
            # Text segment
            seg_path = os.path.join(temp_dir, f"{project_prefix}_{i}.mp3")
            
            # Apply emotion settings
            seg_rate = rate
            seg_vol = "+0%"
            
            if tag in emotions_config:
                seg_rate = emotions_config[tag].get('rate', rate)
                seg_vol = emotions_config[tag].get('volume', '+0%')
            
            # Edge TTS call
            communicate = edge_tts.Communicate(content, voice, rate=seg_rate, volume=seg_vol)
            await communicate.save(seg_path)
            
            if os.path.exists(seg_path):
                clip = AudioFileClip(seg_path)
                audio_clips.append(clip)

        # 3. Join Clips
        if audio_clips:
            final_audio = concatenate_audioclips(audio_clips)
            final_audio.write_audiofile(output_path, logger=None)
            
            # Cleanup
            for clip in audio_clips:
                clip.close()
            
            return True
        return False
        
    except Exception as e:
        print(f"❌ Error en segmentación de audio: {e}")
        return False


async def generate_audio_elevenlabs(text, output_path, voice_id, api_key):
    """Generate audio using ElevenLabs (does NOT support SSML)"""
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


