---
description: AVGL v4.0 Standard - Formato JSON para Guiones de Video (Assets, Objetos, Movimientos)
---

# Reglas del Proyecto AIVideogen (AVGL v4.0)

Este documento es la **Fuente de Verdad** para el formato de guion y estrategias de contenido del proyecto.

## 1. Formato de Guion: AVGL v4.0 (JSON)

El motor y el editor visual funcionan **exclusivamente con JSON**.

### Estructura Base
```json
{
    "title": "Título del Video",
    "voice": "es-ES-AlvaroNeural",      // Voz global
    "background_music": "music.mp3",    // Música fondo
    "blocks": [                         // Array de Bloques
        {
            "title": " Bloque 1",
            "scenes": [                 // Array de Escenas
                {
                    "title": "Gancho",
                    "text": "Texto narrado...",
                    "assets": [         // Array de Objetos Asset
                       { 
                           "id": "imagen.png", 
                           "zoom": "1.0:1.2", 
                           "move": "HOR:50:60" 
                       }
                    ]
                }
            ]
        }
    ]
}
```

## 2. Definición Técnica de Assets

### Regla de Oro: Objetos, NO Strings
❌ INCORRECTO: `"assets": ["imagen.png"]`
✅ CORRECTO:
```json
"assets": [
    {
        "id": "imagen.png",     // Nombre archivo
        "zoom": "1.0:1.3",      // Inicio:Fin (1.0 = 100%)
        "move": "HOR:0:100",    // Ver sintaxis abajo
        "fit": false            // true = Contain, false = Cover
    }
]
```

### Sintaxis de Movimiento (`move`)
Soporta direcciones ortogonales y combinadas. Valores en porcentaje (0-100).

- **Horizontal**: `HOR:start:end` (ej: `HOR:0:100` izquierda a derecha)
- **Vertical**: `VER:start:end` (ej: `VER:100:0` abajo a arriba)
- **Combinado**: `HOR:.. + VER:..` (ej: `HOR:50:50 + VER:0:100`)

## 3. Estrategia de Contenido "Hook-First"

1.  **Gancho (0-3s)**: Frase impactante visual y sonora inmediata.
2.  **Branding**: El logo entra *después* del gancho, nunca antes.
3.  **Ritmo Visual**: Cambios de asset/zoom cada 3-5 segundos.
4.  **Dinamismo**: Usar `zoom` y `move` en el 100% de los assets estáticos.

## 5. Protocolo Pre-Flight de Audio & Assets (Verificación Preventiva)

Antes de generar o lanzar cualquier proyecto de video, **Bill debe ejecutar obligatoriamente**:

1. **Verificación de Existencia Física de Audio**:
   - Para la pista global (`settings.background_music`) y cada pista por bloque (`block.music`), comprobar su presencia en `media/assets/`, `media/music/` o `media/`.
   - Si la pista no existe físicamente en disco, copiarla o generarla antes de iniciar la renderización.
2. **Sincronización de Base de Datos**:
   - Ejecutar la sincronización automática de medios (`sync_media.py`) para registrar las pistas en el modelo `Music` de Django y asegurar su disponibilidad en la interfaz web y el motor.
3. **Calibración de Autoducking & Volúmenes**:
   - Verificar que `music_volume` (rango recomendado: `0.12` a `0.20`) y `audio_ducking_ratio` (rango recomendado: `0.08` a `0.17`) estén explícitamente definidos y activos en los ajustes del guion.
   - Confirmar que ningún bloque tenga `volume = 0` por accidente salvo silencio intencional.

