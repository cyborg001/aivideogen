import imageio.v3 as iio
import os

gif_path = r'c:\Users\hp\aivideogen\aivideogen\media\assets\genghis\acto2\conquista_china_timelapse_v2.gif'

def check_gif_frames():
    if not os.path.exists(gif_path):
        print("Not found")
        return
    
    props = iio.improps(gif_path)
    print(f"Properties: {props}")
    
    frames = iio.imread(gif_path)
    print(f"Number of frames: {len(frames)}")
    if len(frames) > 1:
        import numpy as np
        f0 = frames[0]
        f1 = frames[1]
        diff = np.abs(f0.astype(float) - f1.astype(float)).mean()
        print(f"Diff between frame 0 and 1: {diff:.2f}")

if __name__ == "__main__":
    check_gif_frames()
