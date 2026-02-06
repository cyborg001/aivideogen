from moviepy import VideoFileClip, concatenate_videoclips
import os

p0 = r"C:\Users\hp\aivideogen\aivideogen\media\temp_video\scene_17_0.mp4"
p1 = r"C:\Users\hp\aivideogen\aivideogen\media\temp_video\scene_17_1.mp4"

print(f"Checking {p0}...")
if os.path.exists(p0):
    c0 = VideoFileClip(p0)
    print(f"  Duration: {c0.duration}")
    c0.close()
else:
    print("  File NOT found")

print(f"Checking {p1}...")
if os.path.exists(p1):
    c1 = VideoFileClip(p1)
    print(f"  Duration: {c1.duration}")
    c1.close()
else:
    print("  File NOT found")
