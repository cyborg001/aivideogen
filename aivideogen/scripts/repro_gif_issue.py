import os
from moviepy import VideoFileClip, vfx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

gif_path = r'c:\Users\hp\aivideogen\aivideogen\media\assets\genghis\acto2\conquista_china_timelapse_v2.gif'
output_path = r'c:\Users\hp\aivideogen\aivideogen\media\outputs\test_gif_animation.mp4'

def test_gif_render():
    if not os.path.exists(gif_path):
        print("GIF not found")
        return

    # Load GIF
    v_clip = VideoFileClip(gif_path)
    print(f"Original: dur={v_clip.duration}, fps={v_clip.fps}")
    
    # Apply my suspicious fix v20.6
    if v_clip.fps < 1.0:
        v_clip.fps = 10.0
        print(f"Applied FPS override: {v_clip.fps}")

    # Simulate 10s scene
    duration = 10.0
    required_end = duration
    
    if v_clip.duration < required_end:
        v_clip = v_clip.with_effects([vfx.Loop(duration=required_end + 1.0)])
    
    v_clip = v_clip.subclipped(0, duration)
    
    print(f"Final clip duration: {v_clip.duration}")
    
    # Render small piece
    v_clip.write_videofile(output_path, fps=10, codec="libx264", logger=None)
    print(f"Rendered to {output_path}")
    v_clip.close()

if __name__ == "__main__":
    test_gif_render()
