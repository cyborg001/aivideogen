# 📖 MANUAL COMPLETO - aiVideoGen v2.26.1 (AVGL v4.0)

¡Bienvenido al generador de videos más potente y sencillo! Este sistema transforma guiones JSON en producciones audiovisuales completas utilizando IA avanzada.

## 1. INSTALACIÓN Y ARRANQUE
No necesitas instalar nada. Solo:
1. Extrae el contenido del archivo .zip.
2. Asegúrate de tener un archivo `.env` configurado.
3. Ejecuta `Start_App.bat`.
4. El sistema abrirá automáticamente tu navegador en `http://127.0.0.1:8888`.

## 2. CREACIÓN DE VIDEOS (AVGL v4.0 JSON)
El sistema utiliza un formato JSON estandarizado para máximo control.

### Estructura Básica
```json
{
    "title": "Título del Video",
    "voice": "es-US-AlonsoNeural",
    "speed": 1.0, 
    "pitch": "+0Hz",
    "blocks": [
        {
            "title": "Intro",
            "scenes": [ ... ]
        }
    ]
}
```

### 2.1 Control de Voz y Actuación (NUEVO)
Puedes "dirigir" la actuación de la voz usando dos capas:
1.  **Parámetros Globales (Personaje):**
    *   `speed`: Velocidad (ej. `1.1` es 10% más rápido).
    *   `pitch`: Tono (ej. `+6Hz` más agudo/joven, `-10Hz` más grave/viejo).
2.  **Etiquetas de Emoción (Actuación):**
    Insertadas en el texto para cambiar la intención momentáneamente:
    *   `[TENSO]...[/TENSO]`
    *   `[EPICO]...[/EPICO]`
    *   `[SUSURRO]...[/SUSURRO]`
    *   `[GRITANDO]...[/GRITANDO]`
    *   `[SUSPENSO]...[/SUSPENSO]`

### 2.2 Gestión de Assets e Imágenes
*   **Ruta:** Todos los archivos deben estar en `media/assets/`.
*   **Continuidad (Raccord):** Si una imagen se repite en escenas consecutivas, asegúrate de que el **Zoom final** de la primera coincida con el **Zoom inicial** de la segunda (ej. `1.1` -> `1.1`) para un movimiento fluido.
*   **Overlays:** Puedes añadir efectos visuales como `dust.mp4` o `light_leaks.mp4` en el campo `overlay`.

### 2.3 Subtítulos por Palabra (v3.2)
Los subtítulos se sincronizan automáticamente con las palabras habladas. No necesitas ajustar tiempos manualmente.

## 3. AI HUB (Investigador Automático)
Tu asistente de investigación.
1. Haz clic en "Actualizar Hub".
2. El sistema descarga las últimas noticias de IA y Ciencia.
3. Convierte cualquier noticia en un guion listo para video con un solo clic.

## 4. SOPORTE
Para dudas técnicas avanzadas, consulta `AVGL_MANUAL_v4_JSON.md`.
