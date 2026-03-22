import os
from moviepy import VideoFileClip
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

gif_path = r'c:\Users\hp\aivideogen\aivideogen\media\assets\genghis\acto2\conquista_china_timelapse_v2.gif'

if os.path.exists(gif_path):
    clip = VideoFileClip(gif_path)
    print(f"ORIGINAL - Duration: {clip.duration}, FPS: {clip.fps}")
    
    # Simulate my fix v20.6
    if clip.fps < 1.0:
        clip.fps = 10.0
        print(f"OVERRIDE - New FPS: {clip.fps}, New Duration?: {clip.duration}")
        
    try:
        # Try to get frame at 5 seconds (which should be the 2nd image if original fps=0.33)
        frame_5 = clip.get_frame(5.0)
        print("  Frame at 5.0s: OK")
    except Exception as e:
        print(f"  Error getting frame at 5.0s: {e}")
        
    clip.close()
