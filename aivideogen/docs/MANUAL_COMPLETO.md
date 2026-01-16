# 📖 MANUAL COMPLETO - aiVideoGen v2.22.1

¡Bienvenido al generador de videos más potente y sencillo! Este manual te guiará desde el primer arranque hasta la creación de producciones profesionales.

## 1. INSTALACIÓN Y ARRANQUE
No necesitas instalar nada. Solo:
1. Extrae el contenido del archivo .zip.
2. Asegúrate de tener un archivo `.env` configurado (puedes usar el `.env.example`).
3. Ejecuta `Start_App.bat` (o el `.exe` si está disponible).
4. El sistema abrirá automáticamente tu navegador en `http://127.0.0.1:8888`.

## 2. CREACIÓN DE VIDEOS (Format PRO v2.23)
El corazón de la app es el editor de guiones. Usa el formato de 5 columnas:
`TITULO | IMAGEN | EFECTO | TEXTO | PAUSA`

- **TITULO**: Solo para tu referencia en el editor.
- **IMAGEN**: Nombre del archivo en la carpeta `Assets` (ej: `calle.jpg`).
- **EFECTO**: Controlas el movimiento y la atmósfera. 
  - *Ken Burns*: `HOR`, `VER`, `ZOOM` (ej: `HOR:0:100 + ZOOM:1.0:1.2`).
  - *Overlays*: `OVERLAY:nombre:vol` (ej: `OVERLAY:dust:1`). Volúmenes de 0 a 4 (0 es mudo).
- **TEXTO**: Lo que la voz dirá.
- **PAUSA**: (Opcional) Segundos de silencio tras el texto (ej: `1.5`).
  - Durante las pausas, la música sube automáticamente y el efecto visual continúa.

### 2.2 LIMPIEZA AUTOMÁTICA DE TEXTO (Nuevo v2.25)
El sistema limpia automáticamente el texto antes de generar el audio para evitar que la IA lea cosas extrañas:
- **Etiquetas de Nombre**: `[ETHAN] Hola` -> La IA lee solo "Hola".
- **Acotaciones**: `(Susurrando) Hola` -> La IA lee solo "Hola".
Esto es útil para guiones técnicos donde indicamos quién habla o cómo, pero no queremos que se escuche.
- **Excepción**: Las etiquetas de emoción `[TENSO]...[/TENSO]` SÍ se procesan como instrucciones de voz.

### 2.3 COMENTARIOS Y HASHTAGS (Nuevo)
Puedes usar el símbolo `#` para organizar tu guion o configurar YouTube:
- `# HASHTAGS: #ia #ciencia`: Estos hashtags se usarán automáticamente en la descripción de YouTube (se suman a los que tengas fijos en el `.env`).
- `# MÚSICA: Cinematic`: Sugerencia de estilo que aparecerá en los logs.
- Cualquier línea que empiece con `#` será ignorada por el motor de video.

**Nota de compatibilidad**: El sistema aún soporta el formato antiguo de 4 columnas.

## 3. AI HUB (Investigador de Noticias)
Investiga temas de tendencia automáticamente:

### 🚀 Primera Vez: Fuentes Automáticas
**Cuando presionas "Actualizar Hub" por primera vez**, el sistema añade automáticamente 3 fuentes RSS de alta calidad:
- **Arxiv AI**: Investigación científica en IA (se traduce del inglés).
- **Xataka**: Noticias de tecnología en español.
- **Genbeta**: Software e IA en español.

Esto te permite empezar a investigar inmediatamente sin configuración manual. ¡Pulsa "Actualizar Hub" y en segundos tendrás noticias categorizadas!

### ➕ Añadir tus propias fuentes
1. Ve a "Fuentes RSS".
2. Añade un sitio (ej: Blog de Tecnología). Escribe una **Categoría** (ej: IA).
3. En el Hub, pulsa "Actualizar Hub".
4. Las noticias aparecerán categorizadas automáticamente. ¡Puedes generar un guion desde cualquier noticia con un clic!

## 4. GESTIÓN DE CATEGORÍAS
¡Es inteligente! No tienes que crear categorías manualmente.
- Se crean solas cuando añades una fuente con un nombre de categoría nuevo.
- Se borran solas cuando eliminas todas las fuentes de esa categoría.

## 5. RECURSOS (Música y Assets)
- Coloca tu música en la carpeta `Musica`.
- Coloca tus imágenes y clips en `Assets`.
- El programa los detectará automáticamente para tus proyectos.

---
*Para soporte técnico o configuraciones avanzadas de API, consulta CONFIGURACION.md*
