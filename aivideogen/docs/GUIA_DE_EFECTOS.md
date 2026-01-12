# 🎞️ Guía Maestra de Efectos Visuales (v2.23.0 - Infographic Edition)

Esta guía detalla cómo transformar imágenes estáticas en escenas cinematográficas de alto impacto.

---

## 🏗️ La Estructura de la Escena
`TITULO | IMAGEN | EFECTO | TEXTO | PAUSA`

---

## 🎥 1. Movimientos de Cámara (Ken Burns)

### A. Ejes de Movimiento
- **Horizontal (`HOR`)**: `HOR:Inicio:Fin` (0 a 100).
- **Vertical (`VER`)**: `VER:Inicio:Fin` (0 a 100). *100=Arriba, 0=Abajo.*

### B. Zoom y Encuadre (`ZOOM` & `FIT`)
- **Sintaxis Única de Zoom**: `ZOOM:EscalaInicio:EscalaFin`
  - *Acercar*: `ZOOM:1.0:1.3`
  - *Alejar*: `ZOOM:1.3:1.0`
  - *Estático*: `ZOOM:1.0:1.0`
- **Sintaxis de Ajuste Inteligente (`FIT`)**: 
  - `FIT`: Ajusta la imagen completa a la pantalla (16:9) sin recortar nada. **Obligatorio para infografías y tablas.**

---

## 🌊 2. Overlays Cinematográficos
Añade capas de atmósfera (polvo, grano, luz).

- **Sintaxis**: `OVERLAY:nombre:Volumen`
- **Volumen**: Rango `0` a `10`.
- **Efectos**: `dust`, `grain`, `light_leaks`.
- **Importante**: Si escribes solo `OVERLAY:dust`, el efecto será **mudo**. Usa `:1` para sonido sutil.

---

## 📊 3. Recetario para Infografías
Para que tus datos técnicos se vean perfectos:

1. **Modo Máxima Visibilidad**: `FIT`
2. **Modo Dinámico Seguro**: `FIT + ZOOM:1.0:1.1`
3. **Atmósfera Técnica**: `FIT + OVERLAY:grain:1`

---

## 🚀 4. Ejemplo Combinado Profesional
`FIT + HOR:0:100 + ZOOM:1.0:1.1 + OVERLAY:dust:1`

---

## 💡 Tips
- **Videos (MP4)**: No aceptan movimientos, solo `OVERLAY`.
- **Pausas**: La 5ta columna genera silencios donde la música sube automáticamente.

*Manual oficial v2.23.0*
