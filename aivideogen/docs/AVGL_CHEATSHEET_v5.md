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
  "overlay": "nieve_cayendo.mp4" 
}
```
*Debe existir en `media/overlays/nieve_cayendo.mp4`*

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
