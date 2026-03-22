import os
import imageio.v3 as iio
import numpy as np
from moviepy import ImageSequenceClip, VideoFileClip

gif_path = r'c:\Users\hp\aivideogen\aivideogen\media\assets\genghis\acto2\conquista_china_timelapse_v2.gif'
output_path = r'c:\Users\hp\aivideogen\aivideogen\media\outputs\test_gif_seq.mp4'

def test_image_seq():
    if not os.path.exists(gif_path):
        return

    print("Loading frames with imageio...")
    frames = list(iio.imread(gif_path))
    num_frames = len(frames)
    total_duration = 30.0 # or read from metadata if needed
    fps_val = num_frames / total_duration
    print(f"Loaded {num_frames} frames. Calculated FPS: {fps_val:.4f}")

    # Create ImageSequenceClip
    clip = ImageSequenceClip(frames, fps=fps_val)
    print(f"Clip created. Duration: {clip.duration}")

    # Render small part
    duration = 10.0
    sub = clip.subclipped(0, duration)
    sub.write_videofile(output_path, fps=10, codec="libx264", logger=None)
    
    # Verify
    v = VideoFileClip(output_path)
    f1 = v.get_frame(0.0)
    f2 = v.get_frame(5.0)
    f3 = v.get_frame(9.0)
    
    diff12 = np.abs(f1.astype(float) - f2.astype(float)).mean()
    diff23 = np.abs(f2.astype(float) - f3.astype(float)).mean()
    
    print(f"Difference 0s vs 5s: {diff12:.2f}")
    print(f"Difference 5s vs 9s: {diff23:.2f}")
    
    if diff12 > 1 or diff23 > 1:
        print("SUCCESS: Animation detected with ImageSequenceClip!")
    else:
        print("FAILURE: Still static with ImageSequenceClip")
        
    v.close()
    clip.close()

if __name__ == "__main__":
    test_image_seq()
