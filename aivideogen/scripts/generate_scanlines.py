import cv2
import numpy as np
import os

def generate_scan_lines(width=1080, height=1920, line_gap=2, opacity=0.35):
    """
    Genera un overlay de scanlines con canal alfa para transparencia.
    Optimizado para Shorts (9:16).
    """
    # Crear imagen RGBA (Transparente)
    # 0 = totalmente transparente en el canal alfa
    overlay = np.zeros((height, width, 4), dtype=np.uint8)
    
    # Color de la línea: Blanco (255, 255, 255) con la opacidad indicada
    # Canal 0,1,2 = RGB (255)
    # Canal 3 = ALFA (alpha_val)
    alpha_val = int(255 * opacity)
    
    for y in range(0, height, line_gap * 2): # Ajustamos el salto para el nuevo grosor
        # Dibujar una línea de 2 píxeles de grosor para mejor visibilidad
        overlay[y:y+2, :, 0:3] = 255 # RGB Blanco
        overlay[y:y+2, :, 3] = alpha_val
        
    output_path = r'c:\Users\hp\aivideogen\aivideogen\media\overlays\scan_lines.png'
    
    # Asegurar que el directorio existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Guardar como PNG para mantener transparencia
    cv2.imwrite(output_path, overlay)
    print(f"Overlay generado con exito en: {output_path}")

if __name__ == "__main__":
    generate_scan_lines()
