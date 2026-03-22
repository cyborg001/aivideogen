import os
import sys
import django
import numpy as np
from moviepy import VideoFileClip

# Setup Django
BASE_DIR = r'c:\Users\hp\aivideogen\aivideogen'
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.video_engine import process_video_asset

gif_path = r'c:\Users\hp\aivideogen\aivideogen\media\assets\genghis\acto2\conquista_china_timelapse_v2.gif'
output_path = r'c:\Users\hp\aivideogen\aivideogen\media\outputs\final_verify_gif.mp4'

def verify_fix():
    if not os.path.exists(gif_path):
        print("GIF not found")
        return

    print("Processing GIF with NEW engine logic...")
    # Simulate a 10s scene with the GIF
    target_size = (1920, 1080)
    duration = 10.0
    
    clip = process_video_asset(
        gif_path, duration, target_size,
        clips_to_close=[]
    )
    
    print(f"Clip processed. Duration: {clip.duration}, FPS: {clip.fps}")
    clip.write_videofile(output_path, fps=10, codec="libx264", logger=None)
    
    # Check frames
    v = VideoFileClip(output_path)
    f1 = v.get_frame(0.0)
    f2 = v.get_frame(5.0)
    f3 = v.get_frame(9.0)
    
    diff12 = np.abs(f1.astype(float) - f2.astype(float)).mean()
    diff23 = np.abs(f2.astype(float) - f3.astype(float)).mean()
    
    print(f"Difference 0s vs 5s: {diff12:.2f}")
    print(f"Difference 5s vs 9s: {diff23:.2f}")
    
    if diff12 > 1 or diff23 > 1:
        print("FINAL SUCCESS: Animation detected in the new engine!")
    else:
        print("FINAL FAILURE: Still static in the new engine.")
    
    v.close()
    clip.close()

if __name__ == "__main__":
    verify_fix()
