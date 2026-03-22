import os
import numpy as np
from moviepy import VideoFileClip

video_path = r'c:\Users\hp\aivideogen\aivideogen\media\outputs\test_gif_animation.mp4'

def verify_animation():
    if not os.path.exists(video_path):
        print("Video not found")
        return

    clip = VideoFileClip(video_path)
    print(f"Verifying {video_path} ({clip.duration}s)")
    
    # Get frames at different times
    f1 = clip.get_frame(0.0)
    f2 = clip.get_frame(5.0)
    f3 = clip.get_frame(9.0)
    
    diff12 = np.abs(f1.astype(float) - f2.astype(float)).mean()
    diff23 = np.abs(f2.astype(float) - f3.astype(float)).mean()
    
    print(f"Difference 0s vs 5s: {diff12:.2f}")
    print(f"Difference 5s vs 9s: {diff23:.2f}")
    
    if diff12 > 0.1 or diff23 > 0.1:
        print("SUCCESS: Animation detected (frames are different)")
    else:
        print("FAILURE: Static image detected (frames are identical)")
        
    clip.close()

if __name__ == "__main__":
    verify_animation()
