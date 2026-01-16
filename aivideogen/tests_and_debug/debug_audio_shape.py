import os
import asyncio
import edge_tts
from moviepy import AudioFileClip, AudioClip, concatenate_audioclips
import numpy as np

async def main():
    voice = "es-ES-AlvaroNeural"
    text = "Probando audio."
    output = "debug_shape.mp3"
    
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output)
    
    clip = AudioFileClip(output)
    print(f"Clip Duration: {clip.duration}")
    print(f"Clip nchannels: {clip.nchannels}")
    print(f"Clip FPS: {clip.fps}")
    
    # Let's try to get a frame
    frame = clip.get_frame(0.1)
    print(f"Frame shape: {frame.shape}")
    
    # Test our silence logic
    try:
        # What I wrote in avgl_engine.py
        # silence = AudioClip(lambda t: np.zeros((2, 1)), duration=1.0)
        # Proper way might be:
        silence = AudioClip(lambda t: np.zeros(clip.nchannels), duration=1.0).with_fps(clip.fps)
        print(f"Silence nchannels: {silence.nchannels}")
        
        final = concatenate_audioclips([clip, silence])
        print("Concatenation SUCCESS")
    except Exception as e:
        print(f"Concatenation FAIL: {e}")

if __name__ == "__main__":
    asyncio.run(main())
