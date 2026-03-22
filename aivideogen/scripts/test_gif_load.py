import os
from moviepy import VideoFileClip, ImageClip
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

gif_path = r'c:\Users\hp\aivideogen\aivideogen\media\assets\genghis\acto2\conquista_china_timelapse_v2.gif'

if not os.path.exists(gif_path):
    print(f"ERROR: No existe el archivo en {gif_path}")
else:
    print(f"Archivo encontrado: {gif_path} (Size: {os.path.getsize(gif_path)} bytes)")
    try:
        print("Intentando cargar con VideoFileClip...")
        v_clip = VideoFileClip(gif_path)
        print(f"VideoFileClip ÉXITO: Duración={v_clip.duration}, FPS={v_clip.fps}, Size={v_clip.size}")
        v_clip.close()
    except Exception as e:
        print(f"VideoFileClip FALLÓ: {e}")

    try:
        print("Intentando cargar con ImageClip (por si acaso)...")
        i_clip = ImageClip(gif_path)
        print(f"ImageClip ÉXITO: Size={i_clip.size}")
        i_clip.close()
    except Exception as e:
        print(f"ImageClip FALLÓ: {e}")
