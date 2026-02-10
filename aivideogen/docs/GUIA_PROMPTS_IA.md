# 🤖 Guía de Prompts: Generación de Guiones AVGL v5.0

Para que una IA (como ChatGPT, Gemini o Claude) te ayude a crear guiones perfectos para **AIVideoGen**, copia y pega el siguiente "Master Prompt". Esta guía asegura que el resultado sea 100% compatible con la **versión 5.0** de nuestro motor.

---

## 🚀 El Master Prompt (Copiar y Pegar)

> **Actúa como un experto guionista y editor de video profesional. Tu objetivo es generar un guion técnico en formato JSON compatible con el motor AIVideoGen (AVGL v5.0).**
>
> **REGLAS DE FORMATO:**
> 1. El resultado debe ser un **único objeto JSON**.
> 2. No uses comentarios dentro del JSON.
> 3. Los textos deben incluir **Emotion Tags** como `[TENSO]`, `[EPICO]`, `[SUSPENSO]` o `[GRITANDO]`.
>
> **ESTRUCTURA TÉCNICA (AVGL v5.0):**
> - **Metadata Principal:** `title`, `voice` (ej: `es-ES-AlvaroNeural`), `speed` (1.0).
> - **Bloques:** `title`, `music` (archivo .mp3), `volume` (0.1 a 0.3), `scenes`.
> - **Escenas:** 
>     - `text`: Narración con tags de emoción.
>     - `assets`: Cada escena debe tener un array de assets con:
>         - `type`: Nombre del archivo (ej: `imagen_01.png`).
>         - `video_volume`: (Opcional, solo video) Volumen del audio original (0.0 a 1.0).
>         - `zoom`: `"inicio:fin"` (ej: `"1.0:1.2"`).
>         - `move`: Combinar efectos con `+`. Ej: `"HOR:0:100 + SHAKE:5 + ROTATE:-2:2"`.
>         - `w_rotate`: (Opcional) Rotación constante en grados/seg (ej: `45` para un giro suave).
>         - `overlay`: Pantalla (ej: `"dust"`, `"grain"` o un `.mp4` personalizado).
>     - `sfx`: (Opcional) Array con `type`, `volume` y `offset`.
>     - `pause`: (Opcional) Segundos de silencio al final.
>
> **IMPORTANTE PARA EL USUARIO:**
> - El guion generado usará nombres de archivos genéricos (ej: `escena_1.png`). 
> - **Tú debes crear o descargar estas imágenes/videos** y guardarlos en la carpeta `media/assets/` con el nombre exacto que indique el guion.
>
> **TEMA DEL GUION:**
> [ESCRIBE AQUÍ EL TEMA QUE DESEAS, EJ: "La historia de Stanislav Petrov"]

---

## 🛠️ Cómo Personalizar el Guion

Una vez que la IA te entregue el código, puedes editarlo fácilmente en un editor de texto o dentro de **AIVideoGen**:

### 1. Cambiar Efectos de Movimiento (`move`)
*   **Temblor Cinematográfico:** Añade `+ SHAKE:10` para simular cámara en mano.
*   **Balanceo Suave:** Añade `+ ROTATE:-3:3` para que la imagen oscile ligeramente.
*   **Vórtice (V5.0):** Si quieres que algo gire sin parar (como un planeta o un reloj), usa `"w_rotate": 90`.

### 2. Controlar el Ritmo
*   **Velocidad:** Si sientes que la IA habla muy lento, cambia el valor de `"speed": 1.1` en la metadata principal.
*   **Suspenso:** Aumenta `"pause": 2.0` al final de una escena clave para dejar que la música y el video respiren.

### 3. Emociones de Voz (Edge TTS)
Envuelve tus frases importantes en tags:
*   `[TENSO] ¡El misil ha sido detectado! [/TENSO]`
*   `[EPICO] Es el momento de salvar al mundo. [/EPICO]`

---

## ⚠️ Recordatorio de Assets
**AIVideoGen es el motor que une todo.** 
1. La IA te da el **mapa** (el JSON).
2. Tú debes poner los **ladrillos** (las imágenes y videos en `media/assets/`).
3. Bill (el motor) hace la **magia** del renderizado.

---
**Versión de Guía:** 1.0 | Compatible con **AIVideoGen v8.5+**
