import cv2
import numpy as np
import os

def create_transparent_cockpit(input_path, output_path):
    # Leer imagen
    img = cv2.imread(input_path)
    if img is None:
        print("Error: No se pudo leer la imagen")
        return

    # Convertir a BGRA
    bgra = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    
    # Crear máscara para el "cielo" o ventana (asumiendo que es la parte central y más clara/azulada)
    # Estrategia: Detectar áreas que no son el tablero oscuro
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # El tablero suele ser oscuro. La ventana suele tener contenido generado por la IA.
    # Vamos a usar un threshold para separar el tablero del exterior.
    _, mask = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY)
    
    # Invertir máscara para que el tablero sea blanco y la ventana negra
    # kernel = np.ones((5,5), np.uint8)
    # mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    # Aplicar transparencia a la zona de la ventana (donde la máscara es 1, queremos que sea 0 en alfa)
    # Pero queremos que el tablero (oscuro) sea opaco.
    # Tablero (oscuro < 40) -> Alfa 255
    # Ventana (claro > 40) -> Alfa 0
    bgra[:, :, 3] = np.where(gray < 50, 255, 0).astype(np.uint8)
    
    # Suavizar bordes del canal alfa
    bgra[:, :, 3] = cv2.GaussianBlur(bgra[:, :, 3], (15, 15), 0)

    # Guardar resultado
    cv2.imwrite(output_path, bgra)
    print(f"Overlay guardado en {output_path}")

if __name__ == "__main__":
    src = r"c:\Users\hp\aivideogen\aivideogen\media\assets\cockpit_base.png"
    dst = r"c:\Users\hp\aivideogen\aivideogen\media\assets\cockpit_overlay.png"
    create_transparent_cockpit(src, dst)
