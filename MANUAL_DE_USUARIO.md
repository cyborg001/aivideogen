# 🎬 Manual de Usuario - AI Video Gen (v2.24.0 - Auto-YouTube Edition)

¡Bienvenido a la herramienta definitiva para creación de contenido con IA! Esta versión está diseñada para ofrecer resultados de nivel de estudio de forma automatizada.

---

> [!IMPORTANT]
> **Identidad del Asistente**: Este proyecto está gestionado por **Bill**. Sus reglas de comportamiento, tono y preferencias del Licenciado están guardadas en [identidad_asistente.md](file:///c:/Users/Usuario/Documents/curso%20creacion%20contenido%20con%20ia/reglas/identidad_asistente.md).

---

## ⚡ Estructura del Software

Esta aplicación se divide en dos grandes "cerebros":
1.  **AI Hub (Researcher)**: Investiga noticias, tendencias y gestiona fuentes.
2.  **Generador de Video**: Transforma guiones en piezas audiovisuales con voz, música dinámica e imágenes con movimiento.

---

## 🛠️ Modos de Uso

### 1. Modo Normal (Sin APIs externas)
Ideal para usuarios con guiones propios.
*   **Qué puedes hacer**:
    *   Crear proyectos usando el **Formato Pro** de 5 columnas.
    *   Generar narraciones con el motor gratuito (Edge TTS).
    *   Aplicar efectos Ken Burns manuales.
    *   Subir música y gestionar el **Audio Ducking** automático.

### 2. Modo Power User (IA Full)
Configura tu `GEMINI_API_KEY` en el archivo `.env`.
*   **Investigación Inteligente**: La IA resume noticias por ti.
*   **Generador de Guiones Automático**: Crea scripts de 2 min con un clic.
*   **Estrategia Hook-First**: Guiones optimizados para retención de 2 segundos.

---

## 🎬 Formato de Guion Profesional (v2.22.1)

El sistema utiliza un estándar de 5 columnas separadas por tubos (` | `). 

**Estructura**: `TÍTULO | IMAGEN | EFECTO | TEXTO | PAUSA`

### 1. Las 5 Columnas de Producción
1. **TÍTULO**: Referencia interna (no se lee).
2. **IMAGEN / VIDEO**: Nombre del archivo en la carpeta `Assets` (ej: `city.png`).
3. **EFECTO**: Movimiento y atmósfera (Ken Burns + Overlays).
   - Ej: `ZOOM_IN + OVERLAY:dust`
4. **TEXTO**: El guion que leerá la voz de IA.
5. **PAUSA**: (Opcional) Tiempo de silencio en segundos tras el texto (ej: `1.5`).
   - *Nota*: Durante la pausa, la música sube de nivel automáticamente (**Audio Ducking**).
6. **Regla de Overlays**: Si omites el volumen (ej: `OVERLAY:dust`), el efecto será **mudo**. Usa `OVERLAY:dust:1` para sonido sutil.

### 2. Comentarios y Metadatos (Nuevo)
Puedes añadir notas o configurar redes sociales directamente en el guion usando `#`:
- `# HASHTAGS: #ia #tecnologia`: Configura los hashtags para YouTube automáticamente.
- `# MÚSICA: Epic Cinematic`: Sugerencia de estilo musical (se registra en logs).
- `# Nota: Ignorar esta línea`: Cualquier línea que empiece con `#` no se procesará.

### 3. El Efecto Ken Burns (Columna EFECTO)
Controla el movimiento de tus imágenes fijas:
- **HOR / VER / ZOOM**: Direcciones básicas.
- **Advanced Control**: Usa `DIR:START:END` (Ej: `ZOOM:1.0:1.3`).
- **Overlays**: Añade textura con `OVERLAY:nombre` (Ej: `OVERLAY:grain`).

---

## 🎧 Audio Ducking Inteligente

La aplicación incluye un sistema de mezcla profesional:
- **Atenuación Automática**: La música baja de volumen cuando hay voz (15%) y sube al 100% durante los silencios.
- **Transiciones Suaves (Fades)**: Cambios de volumen de 0.2s para evitar ruidos o chasquidos.

---

## ⚙️ Configuración del archivo `.env`

Abre el archivo `.env` para personalizar tu experiencia:
- **GEMINI_API_KEY**: Cerebro de IA para guiones e investigación.
- **GEMINI_MODEL_NAME**: Especifica el modelo de Gemini a usar. (Por defecto: `gemini-2.5-flash`)
- **ELEVENLABS_API_KEY**: Habilita voces ultra-realistas (opcional).
- **EDGE_VOICE**: Voz por defecto (Ej: `es-DO-EmilioNeural`).
- **PORT**: Puerto donde se lanzará la app (Por defecto: `8888`).
- **MYMEMORY_EMAIL**: Para mejorar la traducción de noticias internacionales.

Aquí tienes un ejemplo de cómo configurar tu archivo `.env`:
```env
GEMINI_API_KEY=tu_api_key_aqui
GEMINI_MODEL_NAME=gemini-2.5-flash
ELEVENLABS_API_KEY=tu_api_key_aqui
EDGE_VOICE=es-DO-EmilioNeural
PORT=8888
MYMEMORY_EMAIL=tu_correo@ejemplo.com
```

> **Modelos de Gemini disponibles (2026)**:
> - `gemini-2.5-flash` - Recomendado (rápido y preciso)
> - `gemini-2.5-pro` - Más potente (más lento)
> - `gemini-2.0-flash-exp-001` - Experimental

---

## 📊 Infografías y Datos Técnicos
Para imágenes que contienen tablas o texto pequeño que **no debe recortarse**:
1. **Evita Paneo (`HOR/VER`)**: El sistema agranda la imagen un 15% para moverla, recortando los bordes.
2. **Modo FIT (NUEVO v2.23)**: Usa la palabra `FIT` en la columna de efecto. Esto ajustará la imagen completa a la pantalla (Letterbox) sin ningún recorte. Ideal para infografías cuadradas.
3. **Usa Zoom Sutil**: `ZOOM:1.0:1.05` es una alternativa si quieres un movimiento mínimo.
4. **Estrategia Pro**: Usa la imagen estática + un `OVERLAY` sutil (ej: `:1`).

---

## 🚀 Estrategia de Contenido (Ley del Gancho)
Para maximizar tus visualizaciones en redes sociales:
1. **Hook (0-2s)**: Empieza con un dato impactante, no con saludos.
2. **Cuerpo**: Cambia de imagen o dirección de Ken Burns cada 3-5 segundos.
3. **Conclusión Profunda**: Aporta un valor reflexivo antes de terminar.
4. **CTA**: Haz una pregunta para generar comentarios.

---
¡Disfruta de la potencia de la producción automatizada! 🚀
