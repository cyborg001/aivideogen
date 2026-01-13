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
    
    # Parse blocks
    blocks_data = data.get("blocks", [])
    if not blocks_data:
        raise ValueError("El script debe tener al menos un 'block'")
    
    for block_data in blocks_data:
        block = AVGLBlock(
            title=block_data.get("title", "Bloque Sin Título"),
            music=block_data.get("music"),
            volume=block_data.get("volume", 0.2)
        )
        
        # Parse scenes
        scenes_data = block_data.get("scenes", [])
        if not scenes_data:
            continue  # Skip empty blocks
        
        for scene_data in scenes_data:
            scene = AVGLScene(title=scene_data.get("title", "Escena Sin Título"))
            scene.text = scene_data.get("text", "")
            scene.voice = scene_data.get("voice", script.voice)
            scene.speed = scene_data.get("speed", script.speed)
            scene.pause = scene_data.get("pause", 0.0)
            
            # Parse assets
            assets_data = scene_data.get("assets", [])
            for asset_data in assets_data:
                asset = AVGLAsset(
                    asset_type=asset_data.get("type"),
                    zoom=asset_data.get("zoom"),
                    move=asset_data.get("move"),
                    overlay=asset_data.get("overlay"),
                    fit=asset_data.get("fit", False)
                )
                scene.assets.append(asset)
            
            # Parse SFX
            sfx_data = scene_data.get("sfx", [])
            for sfx_item in sfx_data:
                sfx = AVGLSFX(
                    sfx_type=sfx_item.get("type"),
                    volume=sfx_item.get("volume", 0.5),
                    offset=sfx_item.get("offset", 0)
                )
                scene.sfx.append(sfx)
            
            block.scenes.append(scene)
        
        script.blocks.append(block)
    
    return script


# ═══════════════════════════════════════════════════════════════════
# Emotion Translator (SSML for Edge TTS)
# ═══════════════════════════════════════════════════════════════════

def translate_emotions(text):
    """
    Translates custom emotion tags like [TENSO] into SSML prosody tags.
    Only works with Edge TTS. ElevenLabs ignores these.
    """
    emotions = {
        'TENSO': {'pitch': '-10Hz', 'rate': '-15%'},
        'EPICO': {'pitch': '+5Hz', 'rate': '+10%', 'volume': '+15%'},
        'SUSPENSO': {'pitch': '-5Hz', 'rate': '-25%'},
        'GRITANDO': {'pitch': '+15Hz', 'rate': '+20%', 'volume': 'loud'},
        'SUSURRO': {'pitch': '-12Hz', 'rate': '-20%', 'volume': '-30%'},
    }
    
    processed_text = text
    for tag, attrs in emotions.items():
        pattern = rf'\[{tag}\](.*?)\[/{tag}\]'
        attr_str = " ".join([f'{k}="{v}"' for k, v in attrs.items()])
        replacement = rf'<prosody {attr_str}>\1</prosody>'
        processed_text = re.sub(pattern, replacement, processed_text, flags=re.IGNORECASE | re.DOTALL)
    
    # Process [PAUSA:X.X] -> <break time="X.Xs"/>
    processed_text = re.sub(r'\[PAUSA:([\d\.]+)\]', r'<break time="\1s"/>', processed_text, flags=re.IGNORECASE)
    
    return processed_text


def wrap_ssml(text, voice, speed="+0%"):
    """
    Wraps text in SSML tags if necessary.
    CRITICAL FIX: Use minimal <speak> tag without attributes (xmlns/version)
    to prevent edge-tts from generating 30s+ of silence/bloat.
    """
    if '<prosody' in text or '<break' in text:
        # Optimization: Only wrap in global prosody if speed is actually changed
        content = text
        if speed != "+0%":
            content = f'<prosody rate="{speed}">{text}</prosody>'
            
        # Minimal wrapper. Do NOT use <voice> tag (handled by communicate param).
        return f'<speak>{content}</speak>'
    return text


# ═══════════════════════════════════════════════════════════════════
# Audio Generation (Edge TTS & ElevenLabs)
# ═══════════════════════════════════════════════════════════════════

async def generate_audio_edge(text, output_path, voice="es-ES-AlvaroNeural", rate="+0%"):
    """Generate audio using Edge TTS (supports SSML)"""
    import edge_tts
    try:
        if text.strip().startswith('<speak'):
            # Already SSML
            communicate = edge_tts.Communicate(text, voice)
        else:
            communicate = edge_tts.Communicate(text, voice, rate=rate)
        
        await communicate.save(output_path)
        return True
    except Exception as e:
        print(f"Error in generate_audio_edge: {e}")
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


