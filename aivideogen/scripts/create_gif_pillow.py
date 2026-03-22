import os
from PIL import Image

# Configuración
assets_dir = r'c:\Users\hp\aivideogen\aivideogen\media\assets\genghis\acto2'
output_path = os.path.join(assets_dir, 'conquista_china_timelapse_v2.gif')

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

# Cargar frames con Pillow
frames = []
for p in image_paths:
    if os.path.exists(p):
        print(f"Procesando {os.path.basename(p)}...")
        img = Image.open(p).convert('RGB')
        # Redimensionar a una base común si fuera necesario (ej. 1024x1024)
        # pero aquí asumimos que ya son consistentes.
        # Si no lo son, Pillow lanzará error al guardar.
        frames.append(img)

if len(frames) < 10:
    print(f"Error: Solo se encontraron {len(frames)} de 10 imágenes.")
else:
    print(f"Guardando GIF: {output_path}")
    # duration=3000 milisegundos = 3 segundos por frame
    # loop=0 significa bucle infinito
    frames[0].save(
        output_path, 
        save_all=True, 
        append_images=frames[1:], 
        duration=3000, 
        loop=0,
        optimize=True
    )
    print(f"¡EXITO! El GIF '{os.path.basename(output_path)}' ha sido creado con 3s de duración por imagen.")
