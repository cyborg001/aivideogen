
import cv2
import numpy as np
import os

def generate_vignette_png(output_path, width=1080, height=1920):
    # 1. Crear una imagen de 4 canales (RGBA)
    # Inicialmente todo negro (0,0,0) y opaco (255)
    img = np.zeros((height, width, 4), dtype=np.uint8)
    
    # 2. Definir el centro y los radios para el gradiente
    center_x, center_y = width // 2, height // 2
    
    # Crear una malla de coordenadas
    x = np.linspace(-1, 1, width)
    y = np.linspace(-1, 1, height)
    xv, yv = np.meshgrid(x, y)
    
    # Calcular la distancia radial desde el centro (0 a ~1.41)
    # Ajustamos para que sea una elipse que encaje en el formato vertical
    dist = np.sqrt(xv**2 + yv**2)
    
    # 3. Mapear la distancia al canal Alfa (0 = transparente, 255 = opaco)
    # Queremos el centro transparente y los bordes negros.
    # Usamos una función de potencia para que el centro sea más amplio y claro.
    alpha = np.clip((dist**2.5) * 255, 0, 255).astype(np.uint8)
    
    # Asignar canales
    img[:, :, 0] = 0   # R
    img[:, :, 1] = 0   # G
    img[:, :, 2] = 0   # B
    img[:, :, 3] = alpha # A (Transparencia)
    
    # 4. Guardar como PNG para preservar el canal Alfa
    cv2.imwrite(output_path, img)
    print(f"✅ Viñeta generada exitosamente en: {output_path}")

if __name__ == "__main__":
    target = r"c:\Users\hp\aivideogen\aivideogen\media\overlays\vignette.png"
    generate_vignette_png(target)
