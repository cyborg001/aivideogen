import os
from PIL import Image

def create_gif(image_paths, output_path, duration=1000):
    images = []
    for path in image_paths:
        if os.path.exists(path):
            img = Image.open(path)
            # Asegurar que todas las imágenes tengan el mismo tamaño (1080x1920 o el de la primera)
            if not images:
                base_size = img.size
            else:
                img = img.resize(base_size, Image.Resampling.LANCZOS)
            images.append(img.convert("RGB"))
    
    if images:
        images[0].save(
            output_path,
            save_all=True,
            append_images=images[1:],
            duration=duration,
            loop=0
        )
        print(f"GIF creado en: {output_path}")
    else:
        print("ERROR: No se encontraron imágenes para el GIF.")

if __name__ == "__main__":
    base_path = r"c:\Users\hp\aivideogen\aivideogen\media\assets\genghis\acto2"
    imgs = [
        os.path.join(base_path, "01_scouts_wall.png"),
        os.path.join(base_path, "02_wall_storm.png"),
        os.path.join(base_path, "03_gobi_camp.png"),
        os.path.join(base_path, "04_cavalry_charge.png"),
        os.path.join(base_path, "05_siege_engines.png"),
        os.path.join(base_path, "06_wall_breach.png"),
        os.path.join(base_path, "07_wall_broken.png"),
        os.path.join(base_path, "08_chinese_city_entry.png"),
        os.path.join(base_path, "09_zhongdu_flames.png"),
        os.path.join(base_path, "10_conquest_view.png")
    ]
    output = os.path.join(base_path, "conquista_china_timelapse.gif")
    create_gif(imgs, output, duration=500) # 0.5s por frame para dinamismo
