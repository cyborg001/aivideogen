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

| Etiqueta | Estilo Nativo Edge (Azure) | Uso Recomendado |
| :--- | :--- | :--- |
| `[TENSO]` | `serious` (-3Hz, -5% rate) | Momentos de peligro inminente, advertencias serias. |
| `[EPICO]` | `excited` (+5Hz, +10% rate) | Clímax de acción, discursos inspiradores. |
| `[SUSPENSO]` | `whispering` (-2Hz, -25% rate) | Misterio, revelaciones lentas. |
| `[GRITANDO]` | `shouting` (+15Hz, +20% rate) | Gritos de batalla, discusiones. |
| `[SUSURRO]` | `whispering` (-5Hz, -20% rate) | Secretos, pensamientos internos. |
| `[PAUSA:X]` | `<break time="Xs"/>` | Insertar silencio exacto (ej. `[PAUSA:2.5]`). |

### Ejemplo Práctico de Guion:

```json
{
    "title": "Scene X",
    "text": "[NARRADOR] Ethan miró el abismo. [SUSURRO] No puedo fallar ahora... [/SUSURRO] [CARLOS] (Con voz grave) [TENSO] ¡Cuidado con el estabilizador! [/TENSO]",
    "voice": "es-DO-EmilioNeural" 
}
```
