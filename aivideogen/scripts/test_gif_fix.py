import os
from moviepy import VideoFileClip, vfx
import numpy as np

gif_path = r'c:\Users\hp\aivideogen\aivideogen\media\assets\genghis\acto2\conquista_china_timelapse_v2.gif'
output_path = r'c:\Users\hp\aivideogen\aivideogen\media\outputs\test_gif_no_fps_override.mp4'

def test_no_override():
    if not os.path.exists(gif_path):
        return

    v_clip = VideoFileClip(gif_path)
    print(f"Original: dur={v_clip.duration}, fps={v_clip.fps}")
    
    # NO FPS OVERRIDE
    
    duration = 10.0
    v_clip = v_clip.subclipped(0, duration)
    
    # Render with a decent output FPS (this shouldn't change the source sampling but the output file)
    v_clip.write_videofile(output_path, fps=10, codec="libx264", logger=None)
    
    # Verify
    clip = VideoFileClip(output_path)
    f1 = clip.get_frame(0.0)
    f2 = clip.get_frame(5.0) # Should be frame 1 or 2 of original GIF (3s delay)
    f3 = clip.get_frame(9.0) # Should be frame 3
    
    diff12 = np.abs(f1.astype(float) - f2.astype(float)).mean()
    diff23 = np.abs(f2.astype(float) - f3.astype(float)).mean()
    
    print(f"Difference 0s vs 5s: {diff12:.2f}")
    print(f"Difference 5s vs 9s: {diff23:.2f}")
    
    if diff12 > 1 or diff23 > 1:
        print("SUCCESS: Animation detected WITHOUT override")
    else:
        print("FAILURE: Still static WITHOUT override")
    
    clip.close()
    v_clip.close()

if __name__ == "__main__":
    test_no_override()
