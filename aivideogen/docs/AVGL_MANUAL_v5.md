# 📘 AVGL v5.0 - MANUAL COMPLETO (JSON)
**Advanced Video Generation Language - Especification v5.0**

---

## 🎯 ¿Qué es AVGL v5.0?

AVGL v5.0 es la evolución del lenguaje de generación de video de **Bill**, diseñado para **Efectos Visuales Avanzados** y máxima robustez.
Mantiene la compatibilidad con v4.0 pero introduce **Dinámicas de Movimiento Complejas** (Rotación, Temblor, Vórtice) y soporte de Assets Personalizados.

---

## 🌟 Novedades en v5.0

| Feature | Sintaxis | Descripción |
| :--- | :--- | :--- |
| **Rotación** | `ROTATE:start:end` | Rota la imagen de un ángulo a otro (interpolación lineal). |
| **Vórtice** | `w_rotate: 360` | Rotación constante por velocidad (grados/segundo). |
| **Temblor** | `SHAKE:intensidad` | Simula cámara en mano o terremoto. |
| **Custom Overlays** | `overlay: "mi_archivo.mp4"` | Carga overlays de video desde `media/overlays/`. |
| **Robustez** | `undefined` -> `0` | El motor repara automáticamente valores corruptos. |

---

## 📋 Esquema JSON Actualizado

```json
{
  "title": "Título del Video",
  "voice": "es-ES-AlvaroNeural",
  "blocks": [
    {
      "title": "Bloque 1",
      "scenes": [
        {
          "title": "Escena con Efectos v5",
          "text": "Esta imagen rota mientras tiembla.",
          "assets": [
            {
              "type": "imagen.png",
              "zoom": "1.0:1.3",
              "move": "HOR:0:100 + SHAKE:10 + ROTATE:-5:5",
              "w_rotate": null, 
              "overlay": "dust"
            }
          ]
        },
        {
          "title": "Efecto Vórtice",
          "text": "Esta galaxia gira indefinidamente.",
          "assets": [
            {
              "type": "galaxy.png",
              "zoom": "1.5",
              "w_rotate": 90, 
              "fit": false
            }
          ]
        }
      ]
    }
  ]
}
```

---

## 🌀 Nuevos Parámetros de Asset

### 1. `move` (Cadena Combinada)
Ahora soporta múltiples efectos concatenados con `+`.

- **Sintaxis**: `"EFECTO:params + EFECTO:params"`
- **Efectos Disponibles**:
    - `HOR:start:end` (Pan Horizontal 0-100%)
    - `VER:start:end` (Pan Vertical 0-100%)
    - `ROTATE:degrees_start:degrees_end` (Rotación Interpolada)
        - Ej: `ROTATE:-10:10` (Balanceo suave)
        - Ej: `ROTATE:0:180` (Media vuelta)
    - `SHAKE:intensity` (Temblor Aleatorio)
        - `intensity`: Pixeles de desplazamiento máx (aprox).
        - Ej: `SHAKE:5` (Sutil), `SHAKE:20` (Terremoto)

### 2. `w_rotate` (Velocidad Angular)
Define una rotación **constante** independiente de la duración de la escena.
Útil para objetos que giran perpetuamente (planetas, relojes, ruedas).

- **Tipo**: `float` (Número)
- **Valor**: Grados por segundo (`deg/s`).
- **Comportamiento**:
    - `90`: Gira 90 grados cada segundo (1 vuelta cada 4s).
    - `360`: Gira 1 vuelta por segundo.
    - `-180`: Gira media vuelta por segundo en sentido antihorario.
- **Nota**: Si se define `w_rotate`, anula cualquier `ROTATE` en `move`.

### 3. `overlay` (Capa Superior)
Ahora soporta archivos personalizados.

- **Antes**: Solo presets (`dust`, `grain`, `scratches`).
- **Ahora**: Cualquier archivo `.mp4` en `media/overlays/`.
    - Ej: `"overlay": "nieve_cayendo.mp4"`
    - Si el archivo no existe, el sistema lo ignora silenciosamente (sin error).

---

## 🛠️ Compatibilidad y Robustez

### Sanitización Automática
Si por error el JSON contiene valores como `undefined`, `null` o texto corrupto en campos numéricos (como `ROTATE:undefined`), AVGL v5.0:
1. Detecta el error.
2. Asume un valor seguro (`0.0`).
3. Continúa el renderizado sin colapsar.

---

> [!TIP]
> **Pro Tip:** Para un "Vórtice Hipnótico", usa `zoom: "1.2"`, `fit: false` y `w_rotate: 45`. El zoom estático ayuda a mantener el centro estable mientras la imagen gira.
