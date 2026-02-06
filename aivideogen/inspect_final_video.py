import os
from moviepy import VideoFileClip

video_path = "c:/Users/hp/aivideogen/aivideogen/media/videos/project_17.mp4"

if not os.path.exists(video_path):
    print(f"File not found: {video_path}")
else:
    try:
        clip = VideoFileClip(video_path)
        print(f"Duration: {clip.duration}")
        print(f"Size: {clip.size}")
        print(f"Has Audio: {clip.audio is not None}")
        if clip.audio:
            print(f"Audio Duration: {clip.audio.duration}")
        clip.close()
    except Exception as e:
        print(f"Error inspecting video: {e}")
