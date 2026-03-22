import os
from moviepy import VideoFileClip, AudioFileClip

v_path = r"c:\Users\hp\aivideogen\aivideogen\media\outputs\ls_171_0.mp4"
a_path = r"c:\Users\hp\aivideogen\aivideogen\media\audio\project_171_scene_000.mp3"

print(f"Buscando Video: {v_path}")
if os.path.exists(v_path):
    clip = VideoFileClip(v_path)
    print(f"DURACION VIDEO: {clip.duration}")
else:
    print("VIDEO NO EXISTE")

print(f"Buscando Audio: {a_path}")
if os.path.exists(a_path):
    aclip = AudioFileClip(a_path)
    print(f"DURACION AUDIO: {aclip.duration}")
else:
    print("AUDIO NO EXISTE")
