# Guía de Voces y Emociones: El Velo Gravitacional (Sistema AVGL)

Este documento define la estrategia de audio para el proyecto, asumiendo el uso de una **voz base (Narrador/Dominicano)** que "actúa" como los demás personajes mediante modulaciones de Pitch (Tono) y Speed (Velocidad).

## 1. Perfiles de Voz (Simulación por Narrador)

Si todo el audiolibro/video es narrado por una sola voz (ej. `es-DO-EmilioNeural`), usaremos estos modificadores para distinguir a los personajes:

| Personaje | Rol | Modificadores Sugeridos (Relativo a la Voz Base) | Efecto Auditivo |
| :--- | :--- | :--- | :--- |
| **NARRADOR** | Base | `Speed: 1.0` \| `Pitch: +0Hz` | Voz neutral, clara y con ritmo estándar. |
| **ETHAN (20 años)** | Protagonista | `Speed: 1.1` \| `Pitch: +6Hz` | Suena más joven, ligero y con cierta urgencia/energía juvenil. |
| **CARLOS (59 años)** | Mentor | `Speed: 0.9` \| `Pitch: -8Hz` | Suena más viejo, pausado, con peso y autoridad paternal. |
| **SONY (Rebelde)** | Antagonista/Aliada | `Speed: 1.15` \| `Pitch: +2Hz` | Habla rápido, tajante, casi interrumpiendo. Tono medio cortante. |
| **MAKO (Vendedor)** | Personaje Secundario | `Speed: 0.85` \| `Pitch: -12Hz` | Suena arrastrado, ronco y pesado (viejo pirata). |

> **Nota Técnica:** Estos valores se añaden a las etiquetas de la escena o se configuran en el editor visual.

---

## 2. Biblioteca de Emociones (Sistema AVGL)

Estas son las etiquetas "nativas" que el sistema `translate_emotions` reconoce y traduce automáticamente a SSML avanzado. Úselas dentro del texto del guion.

| Etiqueta | Configuración Interna | Uso Recomendado |
| :--- | :--- | :--- |
| `[TENSO] ... [/TENSO]` | `Pitch: -10Hz` \| `Rate: -15%` | Momentos de peligro inminente, advertencias serias o miedo contenido. |
| `[EPICO] ... [/EPICO]` | `Pitch: +5Hz` \| `Rate: +10%` \| `Vol: +15%` | Clímax de acción, discursos inspiradores, momentos de victoria. |
| `[SUSPENSO] ... [/SUSPENSO]` | `Pitch: -5Hz` \| `Rate: -25%` | Misterio, revelaciones lentas, narración de ambiente oscuro. |
| `[GRITANDO] ... [/GRITANDO]` | `Pitch: +15Hz` \| `Rate: +20%` \| `Vol: Loud` | Gritos de batalla, discusiones acaloradas, órdenes urgentes. |
| `[SUSURRO] ... [/SUSURRO]` | `Pitch: -12Hz` \| `Rate: -20%` \| `Vol: -30%` | Secretos, pensamientos internos, momentos íntimos o de sigilo. |
| `[PAUSA:X]` | `<break time="Xs"/>` | Insertar silencio exacto (ej. `[PAUSA:2.5]`). |

### Ejemplo Práctico de Guion:

```json
{
    "title": "Scene X",
    "text": "[NARRADOR] Ethan miró el abismo. [SUSURRO] No puedo fallar ahora... [/SUSURRO] [CARLOS] (Con voz grave) [TENSO] ¡Cuidado con el estabilizador! [/TENSO]",
    "voice": "es-DO-EmilioNeural" 
}
```
