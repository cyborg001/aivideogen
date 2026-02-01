# 📖 MANUAL COMPLETO - aiVideoGen v8.5.5 (Estabilidad y Resiliencia)

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

### Estructura de Grupos (Assets Compartidos)
Para mantener la coherencia visual en diálogos o secuencias largas, puedes usar `groups` dentro de un bloque.
Un "grupo" permite definir un **`master_asset`** (imagen o video) que se aplicará automáticamente a todas las escenas del grupo que no tengan su propio asset.

```json
{
    "title": "Conversación en el Garaje",
    "groups": [
        {
            "master_asset": {
                "type": "garaje_fondo.png",
                "zoom": "1.0:1.1",
                "overlay": "dust.mp4"
            },
            "scenes": [
                { "text": "Hola, ¿cómo estás?" }, 
                { "text": "Bien, ¿y tú?" } 
                // Ambas escenas usarán "garaje_fondo.png" automáticamente
            ]
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
    
    > **NUEVO (v2.26.2):** Estas etiquetas ahora usan **Estilos Nativos de Azure** (ej. `shouting`, `whispering`, `excited`) para un realismo superior, además de los ajustes de tono/velocidad.

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

## 4. REGLAS MAESTRAS v8.5 (NUEVO)
Para una calidad profesional de "Noticiero IA", sigue estas reglas:

### 4.1 Fluidez de Narrativa (Conjunciones)
Evita saltos bruscos entre escenas. Al iniciar una nueva escena que continúa el tema anterior, usa conectores: *"Y es que..."*, *"Además..."*, *"Por otro lado..."*.

### 4.2 Inteligencia de Encuadre (Personas)
Si una imagen contiene una persona:
*   **Zoom Out:** Empieza con zoom y termina en `1.0`.
*   **Paneo Vertical:** Usa `MOVE:VER:100:0` para barrer rostros.

### 4.3 YouTube SEO (Auto-Metadatos)
El sistema extrae `fuentes` y `hashtags` automáticamente si están en la raíz del objeto JSON.

---

## 5. RESILIENCIA Y NOTIFICACIONES (v8.5.5)
El sistema incluye mecanismos avanzados para garantizar el éxito del renderizado y la comodidad del usuario.

### 5.1 Alertas Sonoras
El servidor emite notificaciones sonoras nativas al finalizar el proceso:
- ✅ **Éxito**: Sonido "Asterisk" (Ping suave).
- ❌ **Fallo**: Sonido "Hand" (Alerta de error).
Esto permite dejar el renderizado en segundo plano y ser notificado al terminar.

### 5.2 Smart Asset Fallback (Pantalla Negra Zero)
El motor de video es ahora "auto-reparable". Si un asset solicitado no existe:
1. Busca `notiaci_intro_wide.png` o `banner_notiaci.png`.
2. Si no hay fondos oficiales, usa **el primer archivo de imagen** que encuentre en `media/assets`.
3. Evita la aparición de ventanas negras en la producción final.

## 6. SOPORTE
Para dudas técnicas avanzadas, consulta `AVGL_MANUAL_v4_JSON.md`.
