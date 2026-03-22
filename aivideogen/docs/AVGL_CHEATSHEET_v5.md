# 📋 AVGL v5.0 - CHEATSHEET (JSON)

## 🌀 Efectos Visuales Nuevos (Assets)

### 1. Rotación y Temblor
```json
{
  "type": "imagen.png",
  "zoom": "1.0:1.3",
  "move": "HOR:0:100 + ROTATE:-5:5 + SHAKE:10"
}
```

### 2. Vórtice Hipnótico (Velocidad Constante)
```json
{
  "type": "galaxia.png",
  "zoom": "1.5",
  "w_rotate": 360, 
  "fit": false
}
```
*`w_rotate: 360` = 1 vuelta completa por segundo.*

### 3. Custom Overlays
```json
{
  "type": "video.mp4",
  "overlay": "light leaks" 
}
```
*Debe existir en `media/overlays/light leaks.mp4`*

### 4. Audio Master Console (Settings)
```json
{
  "settings": {
    "audio_ducking_ratio": 0.15,
    "audio_attack_time": 0.1,
    "audio_release_time": 0.4,
    "audio_merge_threshold": 1.5,
    "audio_block_fade": 1.0,
    "audio_early_finish": 0.1
  }
}
```

### 5. Social Meta (YouTube/TT)
```json
{
  "settings": {
    "social_title": "Título Gancho",
    "social_desc": "Descripción SEO...",
    "social_tags": "tag1, tag2",
    "social_pinned_comment": "Comentario fijado obligatorio"
  }
}
```

---

## 🏗️ Estructura Completa v5.0

```json
{
  "title": "Mi Video v5",
  "voice": "es-ES-AlvaroNeural",
  "blocks": [
    {
      "title": "Acción",
      "scenes": [
        {
          "title": "Escena Intensa",
          "text": "[GRITANDO]¡Cuidado![/GRITANDO]",
          "assets": [
            {
              "type": "explosion.png",
              "move": "SHAKE:25"
            }
          ]
        }
      ]
    }
  ]
}
```

---

## ⚡ Comandos Rápidos de `move`

- **Panorámica**: `HOR:0:100` (Izq->Der), `VER:0:100` (Arr->Aba)
- **Rotación**: `ROTATE:-10:10` (Balanceo), `ROTATE:0:180` (Giro)
- **Temblor**: `SHAKE:5` (Suave), `SHAKE:25` (Fuerte)
- **Combinado**: `HOR:50:50 + SHAKE:10 + ROTATE:-2:2`

---

## 🎯 Pro Tips v5.0
1. **Vórtice**: Usa `fit: false` y un `zoom` > 1.2 para evitar bordes negros al rotar 360°.
2. **Shake**: Funciona genial en escenas de terror o tensión.
3. **Custom Overlays**: Asegúrate de que el video overlay tenga fondo transparente o modo de fusión (el sistema usa opacidad 0.4 por defecto).
