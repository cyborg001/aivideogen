# 📋 AVGL v4.0 - CHEATSHEET (JSON)

## Estructura Mínima

```json
{
  "title": "Mi Video",
  "blocks": [
    {
      "title": "Bloque 1",
      "scenes": [
        {
          "title": "Escena 1",
          "text": "Texto narrativo",
          "assets": [{"type": "imagen.png"}]
        }
      ]
    }
  ]
}
```

---

## Metadata Global (Opcional)

```json
{
  "title": "El Título",
  "voice": "es-ES-AlvaroNeural",
  "speed": 1.0,
  "style": "neutral"
}
```

---

## Block con Música

```json
{
  "title": "Intro",
  "music": "epic_cinematic.mp3",
  "volume": 0.2,
  "scenes": [...]
}
```


---

## Groups (Assets Compartidos)

```json
{
  "groups": [
    {
      "master_asset": { "type": "fondo.png", "zoom": "1.0:1.1" },
      "scenes": [
        { "text": "Escena 1 (Usa fondo.png)" },
        { "text": "Escena 2 (Usa fondo.png)" }
      ]
    }
  ]
}
```

---


## Scene Completa

```json
{
  "title": "Mi Escena",
  "text": "[TENSO]Texto con emoción[/TENSO]",
  "voice": "es-ES-ElviraNeural",
  "speed": 1.1,
  "assets": [...],
  "sfx": [...],
  "audio": "voces/mi_voz.mp3",
  "pause": 1.5
}
```

---

## Asset: Ken Burns Completo

```json
{
  "type": "imagen.png",
  "zoom": "1.0:1.3",
  "move": "HOR:0:100",
  "overlay": "dust",
  "fit": false
}
```

### Zoom Shortcuts
- Zoom-in: `"1.0:1.5"`
- Zoom-out: `"1.3:1.0"`
- Estático: `"1.0:1.0"` (o no poner)

### Move Options
- `"HOR:0:100"` ← Izq a Der
- `"HOR:100:0"` → Der a Izq
- `"VER:0:100"` ↓ Arriba a Abajo
- `"VER:100:0"` ↑ Abajo a Arriba

### Overlays Disponibles
- `"dust"`
- `"film_grain"`
- `"digital_glitch"`
- `"light_leaks"`

---

## SFX (Efectos de Sonido)

```json
{
  "sfx": [
    {
      "type": "whoosh",
      "volume": 0.5,
      "offset": 0
    }
  ]
}
```

- `offset`: palabras de retraso

---

## Emotion Tags

```json
{
  "text": "[TENSO]urgente[/TENSO] [EPICO]heroico[/EPICO] [SUSPENSO]misterioso[/SUSPENSO]"
}
```

**Tags:**
- `[TENSO]...[/TENSO]`
- `[EPICO]...[/EPICO]`
- `[SUSPENSO]...[/SUSPENSO]`
- `[GRITANDO]...[/GRITANDO]`
- `[SUSURRO]...[/SUSURRO]`

---

## Voces Comunes

- `es-ES-AlvaroNeural` (Masculino, neutro)
- `es-ES-ElviraNeural` (Femenino, claro)
- `es-MX-DaliaNeural` (Mexicano, femenino)
- `es-AR-ElenaNeural` (Argentino, femenino)

---

## Speed (Velocidad)

- `0.9` = -10% (más lento)
- `1.0` = Normal
- `1.1` = +10% (más rápido)
- `1.2` = +20% (muy rápido)

---

## 🎯 Pro Tips

1. **Herencia:** Los scenes heredan `music`, `voice`, `speed` del block.
2. **Grupos:** Puedes heredar `voice`, `speed` y `audio` (voz real) desde un `group`.
3. **Pause:** Siempre al final de la escena.
4. **Offset SFX:** `0` = inicio, `5` = después de 5 palabras.
5. **Overlays:** Menos es más - no abuses.

---

## ✅ Template Rápido

```json
{
  "title": "TÍTULO_AQUÍ",
  "voice": "es-ES-AlvaroNeural",
  "blocks": [
    {
      "title": "Intro",
      "music": "epic.mp3",
      "volume": 0.2,
      "scenes": [
        {
          "title": "Hook",
          "text": "¿Sabías que...?",
          "assets": [
            {
              "type": "imagen1.png",
              "zoom": "1.0:1.3",
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

> [!NOTE]
> Este formato es **100% validable** con herramientas JSON estándar. ¡Sin errores de sintaxis!
