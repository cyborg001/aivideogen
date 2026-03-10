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
| **Master Console** | `audio_block_fade: 1.0` | Control profesional de audio por proyecto (Ducking, Fades). |
| **Social Persistence** | `social_title` | Persistencia de metadatos de YouTube/TikTok en el editor. |
| **Teleprompter** | `Studio Recorder` | Lectura de guion integrada en el modal de grabación. |
| **Forzar Duración** | `force_duration: true` | Permite sobreescribir la duración estimada recortando o pausando el clip. |
| **Robustez** | `undefined` -> `0` | El motor repara automáticamente valores corruptos. |

---

## 📋 Esquema JSON Actualizado

```json
{
  "title": "Título del Video",
  "voice": "es-ES-AlvaroNeural",
  "settings": {
    "audio_ducking_ratio": 0.12,
    "audio_attack_time": 0.1,
    "audio_block_fade": 1.0,
    "social_title": "Mi Gran Video",
    "social_tags": "ia, video, tech"
  },
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

- **Antes**: Solo presets (`dust`, `grain`).
- **Ahora**: Cualquier archivo `.mp4` en `media/overlays/` (ej: `light leaks`).
    - Ej: `"overlay": "light leaks"`
    - Si el archivo no existe, el sistema lo ignora silenciosamente (sin error).

### 4. `force_duration` y `duration` (Forzado de Tiempo)
Permite ignorar la duración calculada automáticamente (basada en el audio TTS o MP3) y fijar una duración exacta para la escena o el grupo.

- **Tipo**: `boolean` (`force_duration`) y `float` (`duration`).
- **Valores**: 
    - `force_duration`: `true` o `false`.
    - `duration`: Número de segundos (ej: `5.5`).
- **Comportamiento**:
    - **Si el audio es más largo**: El renderizador cortará (clipping) el audio y el video en el momento exacto definido.
    - **Si el audio es más corto**: Se completará la duración reproduciendo el audio y luego manteniendo el último frame de video en silencio hasta alcanzar el tiempo.
    - **A nivel de Grupo (Master Shot)**: Si un grupo entero tiene `force_duration`, el motor comprimirá escalarmente la duración de todas las escenas hijas para que su suma no exceda esta duración forzada.

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
