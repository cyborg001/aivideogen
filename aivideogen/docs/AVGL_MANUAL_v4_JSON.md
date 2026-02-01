# 📘 AVGL v4.0 - MANUAL COMPLETO (JSON)
**Advanced Video Generation Language - Formato JSON**

---

## 🎯 ¿Qué es AVGL v4.0?

AVGL v4.0 es el lenguaje nativo de **Bill** (el motor de generación de video) pero en formato **JSON**, lo que lo hace más robusto, validable y compatible con IA.

---

## 🏗️ Estructura Jerárquica

```
Script (Raíz)
  ├── Metadata (título, voz global, velocidad)
  └── Blocks (Bloques/Capítulos)
       └── Scenes (Escenas individuales)
            ├── Text (narración con [EMOTION] tags)
            ├── Assets (imágenes/videos con efectos)
            ├── SFX (efectos de sonido)
            ├── Pause (silencios)
            ├── Audio (voz real personalizada)
            └── Voice Override (cambio de voz específico)
```

---

## 📋 Esquema JSON Completo

```json
{
  "title": "Título del Video",
  "voice": "es-ES-AlvaroNeural",
  "speed": 1.0,
  "style": "neutral",
  "blocks": [
    {
      "title": "Nombre del Bloque",
      "music": "nombre_pista.mp3",
      "volume": 0.2,
      "scenes": [
        {
          "title": "Nombre de la Escena",
          "text": "Texto narrativo con [EMOTION]tags[/EMOTION]",
          "voice": "es-ES-ElviraNeural",
          "speed": 1.1,
          "assets": [
            {
              "type": "imagen.png",
              "zoom": "1.0:1.3",
              "move": "HOR:0:100",
              "overlay": "dust",
              "fit": false
            }
          ],
          "sfx": [
            {
              "type": "whoosh",
              "volume": 0.5,
              "offset": 0
            }
          ],
          "audio": "voces/mi_voz_real.mp3",
          "pause": 1.5
        }
      ]
    }
  ]
}
```

---

## 🎬 Nivel 1: Metadata del Script (Raíz)

```json
{
  "title": "El Despertar de la IA",
  "voice": "es-ES-AlvaroNeural",
  "speed": 1.0,
  "style": "neutral"
}
```

### Atributos opcionales:
- `title`: Título del video (sobrescribe el título de la UI)
- `voice`: Voz predeterminada para todo el video
- `speed`: Velocidad global (1.0 = normal, 1.2 = +20%)
- `style`: Estilo de narración (`neutral`, `cheerful`, `sad`)

---

## 📦 Nivel 2: Blocks (Bloques/Capítulos)

```json
{
  "blocks": [
    {
      "title": "Intro Impactante",
      "music": "epic_cinematic.mp3",
      "volume": 0.2,
      "scenes": [...]
    }
  ]
}
```

### Atributos:
- `title`: Nombre del bloque (aparece en timestamps de YouTube)
- `music`: Archivo de música de fondo (hereda a las escenas)
- `volume`: Volumen de la música (0.0 a 1.0)
- `scenes`: Array de escenas

**Herencia:** Las escenas heredan `music`, `voice`, `speed` del bloque (si no especifican lo contrario).


---

## 🏗️ Nivel 2.5: Groups (Assets Compartidos)

Dentro de un `block`, puedes usar `groups` para agrupar escenas que comparten un mismo escenario o asset visual principal. Esto evita repetir el código del asset en cada escena y facilita el mantenimiento.

### Estructura de Grupo
```json
{
  "blocks": [
    {
      "title": "Capítulo 1",
      "groups": [
        {
          "title": "Conversación en Cafetería",
          "master_asset": {
            "type": "cafeteria_bg.png",
            "zoom": "1.0:1.1",
            "overlay": "dust"
          },
          "scenes": [
            { 
              "title": "Saludo", 
              "text": "Hola, ¿cómo estás?",
              "voice": "es-ES-ElviraNeural"
            },
            { 
              "title": "Respuesta", 
              "text": "Todo bien por aquí.",
              "voice": "es-ES-AlvaroNeural"
            }
          ]
        }
      ]
    }
  ]
}
```

### Reglas de Herencia:
156: 1.  **Herencia Visual**: Todas las escenas dentro del grupo heredarán automáticamente el `master_asset` (incluyendo zoom, move, overlay) **SOLO SI** la escena no define sus propios `assets`.
157: 2.  **Herencia de Audio/Voz**: Puedes definir `voice`, `speed` y `audio` a nivel de grupo. Las escenas los heredarán si no tienen sus propios valores.
158: 3.  **Override**: Si una escena dentro del grupo define su propio array `assets`, este tendrá prioridad y el `master_asset` será ignorado para esa escena específica.
159: 4.  **Interpolación**: Bill intenta mantener la continuidad visual entre escenas del mismo grupo para evitar saltos bruscos en el zoom (raccord).

---


## 🎞️ Nivel 3: Scenes (Escenas)

### Escena Básica
```json
{
  "title": "Hook Directo",
  "text": "¿Sabías que la IA acaba de lograr algo increíble?",
  "assets": [
    {
      "type": "ai_brain_glowing.png"
    }
  ]
}
```

### Escena Avanzada con Todo
```json
{
  "title": "Revelación Épica",
  "text": "[TENSO]El tiempo se agota[/TENSO] y la humanidad debe decidir.",
  "voice": "es-ES-ElviraNeural",
  "speed": 1.1,
  "assets": [
    {
      "type": "doomsday_clock.png",
      "zoom": "1.0:1.5",
      "move": "VER:20:80",
      "overlay": "dust"
    }
  ],
  "sfx": [
    {
      "type": "clock_ticking",
      "volume": 0.3,
      "offset": 2
    }
  ],
  "pause": 1.0
}
```

### Atributos de Scene:
- `title`: **Obligatorio**. Nombre de la escena
- `text`: Texto narrativo (puede incluir [EMOTION] tags)
- `voice`: Voz específica (sobrescribe la del bloque/script)
- `speed`: Velocidad específica
- `assets`: Array de activos visuales
- `sfx`: Array de efectos de sonido
- `pause`: Segundos de silencio al final de la escena

---

## 🖼️ Assets (Activos Visuales)

### Asset Estático Simple
```json
{
  "type": "space_station.png"
}
```

### Asset con Ken Burns (Zoom + Pan)
```json
{
  "type": "earth_from_space.png",
  "zoom": "1.0:1.3",
  "move": "HOR:0:100"
}
```

### Asset con Overlay Cinematográfico
```json
{
  "type": "laboratory_dark.png",
  "zoom": "1.1:1.0",
  "overlay": "dust"
}
```

### Asset con TODO
```json
{
  "type": "mars_landscape.png",
  "zoom": "1.2:1.5",
  "move": "VER:30:70",
  "overlay": "film_grain",
  "fit": false
}
```

### Parámetros de Asset:

#### `type` (obligatorio)
- Nombre del archivo (debe existir en `media/assets/`)
- Soporta: `.png`, `.jpg`, `.jpeg`, `.mp4`

#### `zoom` (opcional)
- Formato: `"start:end"` (ej: `"1.0:1.3"`)
- Zoom-in: `"1.0:1.5"` (más cercano al final)
- Zoom-out: `"1.3:1.0"` (más lejano al final)

#### `move` (opcional)
- `"HOR:0:100"` - Pan horizontal (izquierda → derecha)
- `"HOR:100:0"` - Pan horizontal (derecha → izquierda)
- `"VER:0:100"` - Pan vertical (arriba → abajo)
- `"VER:100:0"` - Pan vertical (abajo → arriba)

#### `overlay` (opcional)
- Archivos en `media/overlays/`
- Ejemplos: `"dust"`, `"film_grain"`, `"digital_glitch"`, `"light_leaks"`

#### `fit` (opcional, default: false)
- `false`: Cubre todo el frame (puede recortar)
- `true`: Ajusta sin recortar (puede dejar barras negras)

---

## 🔊 SFX (Efectos de Sonido)

```json
{
  "sfx": [
    {
      "type": "whoosh",
      "volume": 0.5,
      "offset": 0
    },
    {
      "type": "impact",
      "volume": 0.8,
      "offset": 3
    }
  ]
}
```

### Parámetros:
- `type`: Nombre del archivo SFX (en `media/sfx/`)
- `volume`: 0.0 (silencio) a 1.0 (máximo)
- `offset`: Palabras de retraso antes de reproducir

---

## ⏸️ Pause (Silencios Dramáticos)

```json
{
  "pause": 1.5
}
```

- Se ejecuta **al final** de la narración de la escena
- Útil para dar suspenso antes de la siguiente escena

---

## 🎙️ Audio (Voz Real Personalizada)

Si tienes una locución grabada profesionalmente o quieres usar una voz personalizada que no sea TTS (Text-to-Speech), puedes usar el campo `audio`.

```json
{
  "audio": "voces/locucion_pro.mp3"
}
```

- **Ruta**: Relativa a `media/assets/` o absoluta.
- **Efecto**: Si se define, Bill **ignorará el campo `text`** (no generará TTS) para esa escena y usará el archivo de audio subido.
- **Herencia**: Puedes definirlo en un `group` para aplicarlo a varias escenas.

---

## 🎭 Emotion Tags (Tags de Emoción)

En el campo `text`, puedes usar tags especiales para controlar el tono:

```json
{
  "text": "[TENSO]El tiempo se agota...[/TENSO] pero aún hay esperanza."
}
```

### Tags Disponibles:
- `[TENSO]...[/TENSO]` - Voz tensa, urgente
- `[EPICO]...[/EPICO]` - Voz heroica, grandiosa
- `[SUSPENSO]...[/SUSPENSO]` - Voz misteriosa, lenta
- `[GRITANDO]...[/GRITANDO]` - Voz fuerte, emocionada
- `[SUSURRO]...[/SUSURRO]` - Voz baja, íntima

**Nota:** Solo funciona con Edge TTS. ElevenLabs los ignora.

---

## 📝 Ejemplo Completo: Video Profesional

```json
{
  "title": "El Amanecer de la IA",
  "voice": "es-ES-AlvaroNeural",
  "speed": 1.05,
  "blocks": [
    {
      "title": "Intro: El Despertar",
      "music": "epic_tension.mp3",
      "volume": 0.15,
      "scenes": [
        {
          "title": "Hook Impactante",
          "text": "[TENSO]¿Sabías que la IA acaba de superar a los humanos en algo que creíamos imposible?[/TENSO]",
          "assets": [
            {
              "type": "ai_brain_hologram.png",
              "zoom": "1.0:1.4",
              "move": "HOR:0:100",
              "overlay": "digital_glitch"
            }
          ],
          "sfx": [
            {
              "type": "whoosh_dramatic",
              "volume": 0.6,
              "offset": 0
            }
          ]
        },
        {
          "title": "La Revelación",
          "text": "DeepMind acaba de anunciar que su nueva IA, [GRITANDO]Gemini Ultra 2.0[/GRITANDO], puede razonar como un ser humano.",
          "assets": [
            {
              "type": "deepmind_lab.png",
              "zoom": "1.2:1.0",
              "move": "VER:30:70"
            }
          ],
          "pause": 1.0
        }
      ]
    }
  ]
}
```

---

## 🔊 Mezcla de Audio y Ducking (v6.5)

Bill gestiona automáticamente el volumen de la música de fondo para que la voz siempre sea clara. A partir de la v6.5, el sistema soporta **Ducking Granular**, lo que permite que la música suba incluso durante las pausas internas (`[PAUSA:X]`) de una escena.

### Configuración en `.env`
Puedes ajustar el comportamiento del audio mediante estas variables:

- `AUDIO_DUCKING_RATIO`: Nivel al que baja la música (0.10 = 10% del volumen original).
- `AUDIO_ATTACK_TIME`: Segundos que tarda la música en BAJAR al empezar a hablar.
- `AUDIO_RELEASE_TIME`: Segundos que tarda la música en SUBIR durante los silencios.

### Perfiles Recomendados
Dependiendo del tipo de contenido, puedes configurar estos valores en tu `.env`:

| Perfil | Attack | Release | Ratio | Uso Ideal |
| :--- | :--- | :--- | :--- | :--- |
| **Dinámico/Vlog** | 0.15s | 0.4s | 0.12 | Ritmo rápido, pausas cortas (0.5s). |
| **Documental** | 0.3s | 0.8s | 0.10 | Narración pausada, tono serio. |
| **Relajado/Zen** | 0.5s | 1.5s | 0.05 | Transiciones lentas y música suave. |

> [!IMPORTANT]
> **Regla de Oro:** Si tus guiones tienen pausas cortas (0.5s) y quieres que la música se note, usa el perfil **Dinámico** con un `Release` de **0.4s**.

---

## 🎯 Mejores Prácticas

### ✅ DO (Hacer)
- Usa nombres de archivo descriptivos en `assets`
- Combina zoom + pan para dinamismo
- **Raccord de Zoom**: Si repites imagen, inicia el zoom donde terminó el anterior (ej. 1.1 -> 1.1)
- **Overlay Continuo**: Mantén el mismo overlay en escenas consecutivas del mismo lugar
- Usa `pause` para momentos dramáticos
- Alterna voces en diálogos (`voice` override)

### ❌ DON'T (Evitar)
- No rompas el movimiento (ej. terminar en zoom 1.4 y saltar a 1.0 en la misma imagen)
- No abuses de `[EMOTION]` tags - úsalos estratégicamente
- No pongas `pause` muy largos (>3 seg) - aburren
- No combines demasiados overlays en una misma escena

---

## 🔄 Migración desde XML

### Antes (XML):
```xml
<scene title="Hook">
  <asset type="imagen.png" zoom="1.0:1.3" move="HOR:0:100" />
  ¿Sabías que...?
</scene>
```

### Después (JSON):
```json
{
  "title": "Hook",
  "text": "¿Sabías que...?",
  "assets": [
    {
      "type": "imagen.png",
      "zoom": "1.0:1.3",
      "move": "HOR:0:100"
    }
  ]
}
```

---

## 🛠️ Validación

Bill validará automáticamente:
- ✅ Sintaxis JSON correcta
- ✅ Archivos de assets existen
- ✅ Voces válidas
- ✅ Valores numéricos en rangos correctos

**Si hay error**, Bill te dirá exactamente en qué línea está el problema.

---

> [!TIP]
> **Pro Tip:** Usa un editor JSON con validación (como VS Code) para escribir tus scripts. ¡Bill te lo agradecerá! 🎬✨
