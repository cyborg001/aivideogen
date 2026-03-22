import os
from moviepy import VideoFileClip
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

gif_path = r'c:\Users\hp\aivideogen\aivideogen\media\assets\genghis\acto2\conquista_china_timelapse_v2.gif'

if os.path.exists(gif_path):
    clip = VideoFileClip(gif_path)
    print(f"GIF: {os.path.basename(gif_path)}")
    print(f"  Duration: {clip.duration}")
    print(f"  FPS: {clip.fps}")
    print(f"  Size: {clip.size}")
    
    # Try to get frame at 0.5s if duration allows
    try:
        frame = clip.get_frame(0.1)
        print("  Frame at 0.1s: OK")
    except Exception as e:
        print(f"  Error getting frame: {e}")
    
    clip.close()
else:
    print(f"File not found: {gif_path}")
