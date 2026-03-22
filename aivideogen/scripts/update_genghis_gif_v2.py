import os
import imageio.v2 as imageio
from PIL import Image
import numpy as np

# Configuración
assets_dir = r'c:\Users\hp\aivideogen\aivideogen\media\assets\genghis\acto2'
output_path = os.path.join(assets_dir, 'conquista_china_timelapse_3s.gif')

# Lista de imágenes (ordenadas por el prefijo numérico)
images = [
    '01_scouts_wall.png',
    '02_wall_storm.png',
    '03_gobi_camp.png',
    '04_cavalry_charge.png',
    '05_siege_engines.png',
    '06_wall_breach.png',
    '07_wall_broken.png',
    '08_chinese_city_entry.png',
    '09_zhongdu_flames.png',
    '10_conquest_view.png'
]

image_paths = [os.path.join(assets_dir, img) for img in images]

# Verificar existencia y cargar imágenes
frames = []
target_size = None

for p in image_paths:
    if os.path.exists(p):
        print(f"Cargando {os.path.basename(p)}...")
        img = Image.open(p)
        
        if target_size is None:
            target_size = img.size # (width, height)
        
        if img.size != target_size:
            img = img.resize(target_size, Image.Resampling.LANCZOS)
        
        # Convertir a RGB
        frames.append(np.array(img.convert('RGB')))

if len(frames) < 10:
    print(f"Error: Solo se encontraron {len(frames)} de 10 imágenes.")
else:
    print(f"Generando NUEVO GIF con duración de 3.0s por frame...")
    # duration=3.0 (segundos por frame en imageio v2)
    imageio.mimsave(output_path, frames, duration=3.0, loop=0)
    print(f"¡Nuevo GIF generado con éxito en: {output_path}!")
