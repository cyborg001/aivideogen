"""
Guion de prueba para el nuevo sistema HOR/VER + ZOOM
Copia este contenido en la web app para probar los efectos
"""

print("""
FORMATO: TITULO | IMAGEN | EFECTO | TEXTO

Ejemplos de efectos disponibles:
---------------------------------

1. MOVIMIENTO HORIZONTAL:
   HOR:0:100    # Izquierda a derecha completo
   HOR:100:0    # Derecha a izquierda completo
   HOR:20:80    # Movimiento parcial

2. MOVIMIENTO VERTICAL:
   VER:0:100    # Arriba a abajo completo
   VER:100:0    # Abajo a arriba completo
   VER:30:70    # Movimiento parcial

3. ZOOM SIMPLE:
   ZOOM_IN      # Acercamiento suave (1.0x → 1.3x)
   ZOOM_OUT     # Alejamiento suave (1.3x → 1.0x)

4. ZOOM PERSONALIZADO:
   ZOOM_IN:1.0:2.0      # Acercar al 200%
   ZOOM_OUT:1.5:1.0     # Alejar desde 150%

5. COMBINADOS:
   HOR:20:80+ZOOM_IN             # Pan horizontal + zoom
   VER:30:70+ZOOM_OUT:1.5:1.0    # Pan vertical + zoom personalizado

6. SIN EFECTO:
   (Dejar vacío)  # Imagen estática

---------------------------------

GUION DE PRUEBA PARA COPIAR:
""")

script = """Prueba Horizontal Derecha | imagen1.png | HOR:0:100 | Este efecto mueve la imagen de izquierda a derecha
Prueba Horizontal Izquierda | imagen2.png | HOR:100:0 | Este efecto mueve la imagen de derecha a izquierda
Prueba Vertical Abajo | imagen3.png | VER:0:100 | Este efecto mueve la imagen de arriba hacia abajo
Prueba Vertical Arriba | imagen4.png | VER:100:0 | Este efecto mueve la imagen de abajo hacia arriba
Prueba Zoom In | imagen5.png | ZOOM_IN | Este efecto hace un acercamiento suave
Prueba Zoom Out | imagen6.png | ZOOM_OUT | Este efecto hace un alejamiento suave
Prueba Zoom Extremo | imagen7.png | ZOOM_IN:1.0:2.5 | Este efecto hace un zoom extremo al 250 porciento
Prueba Combinado | imagen8.png | HOR:20:80+ZOOM_IN | Este efecto combina movimiento horizontal con zoom
Imagen Estática | imagen9.png |  | Esta imagen no tiene ningún efecto de movimiento"""

print(script)

print("""

---------------------------------
✅ Copia el guion de arriba (sin la primera y última línea de guiones)
✅ Pégalo en la web app en el campo "Script"
✅ Asegúrate de tener imágenes con esos nombres en tu carpeta de assets
✅ Genera el video y prueba los efectos
""")
