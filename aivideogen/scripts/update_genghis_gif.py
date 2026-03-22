import os
from moviepy import ImageSequenceClip

# Configuración
assets_dir = r'c:\Users\hp\aivideogen\aivideogen\media\assets\genghis\acto2'
output_path = os.path.join(assets_dir, 'conquista_china_timelapse.gif')

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

# Verificar existencia
valid_paths = [p for p in image_paths if os.path.exists(p)]

if len(valid_paths) < 10:
    print(f"Error: Solo se encontraron {len(valid_paths)} de 10 imágenes.")
else:
    # Crear clip con 3 segundos por imagen (durations=[3, 3, ...])
    # durations puede ser una lista de duraciones o MoviePy puede manejar fps.
    # Para 3s por imagen, fps = 1/3
    clip = ImageSequenceClip(valid_paths, fps=1/3)
    
    print(f"Generando GIF en: {output_path}")
    clip.write_gif(output_path, fps=10) # fps aquí es la fluidez del GIF final, no la velocidad de cambio
    clip.close()
    print("¡GIF actualizado con éxito! (3 segundos por imagen)")
