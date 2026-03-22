# 📑 Reglas de Oro - NotiACI

Este documento contiene las reglas fundamentales de identidad y operación para el proyecto NotiACI. Estas reglas deben seguirse estrictamente en cada generación.

## 👤 Identidad y Marca
- **Saludo Oficial**: En videos largos y descripciones, el saludo debe ser: **"¡Hola! Bienvenidos a mi canal"**.
  - **Excepciones**:
    1. En **Shorts/TikTok**, se omite el saludo para ir directo al grano.
    2. En la **Serie Leyendas**, se omite el saludo para no romper la atmósfera épica y entrar directamente en la narrativa.
- **Tono**: Profesional, proactivo y preciso.
- **Audiencia**: Arquitectos de contenido y entusiastas de la IA y ciencia.

## 🎬 Estrategia de Contenido (Hook-First)
1. **El Gancho (0-2s)**: Impacto directo con la noticia.
2. **Identidad**: En videos largos, el saludo de marca viene inmediatamente después del gancho inicial. En **Shorts**, la identidad se transmite por el ritmo y los assets.
3. **Ritmo Visual**: Cambio de escenas cada 2-4 segundos.
4. **Cierre**: Pregunta provocadora para fomentar comentarios y suscripción.
5. **Bloque CTA Estándar (@cyborg001)**: Todos los videos largos deben finalizar con un bloque de cierre estructurado:
    1. **Escena 1 (Suscripción)**: Mensaje directo invitando a suscribirse y activar la campana (formato `[TITLE:SUSCRÍBETE]`).
    2. **Escena 2 (Outro)**: Un segmento de **60 segundos exactos** compuesto por un montaje visual (pueden ser imágenes del video o timelapses) acompañado exclusivamente por la música favorita del canal (**Im_Giving_Up_-_Everet_Almond.mp3**) sin narración de voz. Esto permite al espectador procesar la información y conecta emocionalmente con la marca.

## 🎨 Estándares Visuales
1. **Encuadre Completo**: Las imágenes deben **completar el cuadro** (Full-frame). Evitar bordes blancos, letterboxing o composiciones incompletas.
2. **Estilo**: Uso de "Epic graphic novel art" o "Cinematic concept art" para mantener la atmósfera épica.
3. **Composición**: Priorizar formatos panorámicos y composiciones cinematográficas que llenen el área de visión.
4. **Rescate de Assets**: Tras generar o descargar imágenes, es **obligatorio** realizar una auditoría del historial y el "brain" (contexto) para asegurar que ningún asset generado sea omitido. Cada imagen es "oro" y debe ser integrada o justificada su exclusión.
5. **Barrido Inteligente (Panning)**: Si una imagen es cuadrada (1:1) en un video panorámico (16:9), el espacio excedente tras llenar el encuadro es **Vertical**. En este caso, se debe usar **`VER:0:100`** para recorrer la imagen de arriba a abajo.
    - **Solo usar HOR** si la imagen es específicamente panorámica (ej. generado como ultrawide). 
    - El objetivo es eliminar la estática y mostrar el detalle oculto en la dimensión con "aire".

## 🛠️ Protocolos Operativos
- **Planificación Primero**: Nunca realizar ediciones sin presentar un plan aprobado.
- **Etiquetas de Dicción (`[PHO]`)**: Siguen el formato `[PHO]palabra[/PHO]`. Se deben usar obligatoriamente para:
    1. Palabras en idiomas extranjeros (Mongol, Chino, etc.).
    2. Siglas o acrónimos.
    3. Términos que requieren un énfasis especial o una pronunciación precisa por el TTS.
- **Etiquetas de Texto en Pantalla (`[TITLE]`)**: Se usan para resaltar conceptos clave, nombres de personajes al presentarlos o títulos de bloques (e.g., `[TITLE:LA GRAN MURALLA]`). Ayudan a la visualización mental y estructural del video.
- **Ritmo y Pausas**: Aunque se prioriza la puntuación natural, el uso de etiquetas `[PAUSA:0.5]` es **permitido y recomendado** en videos narrativos largos para crear suspenso, enfatizar revelaciones o dar aire a descripciones complejas.
- **Verificación Sistemática**: Probar cambios y documentar resultados.
- **Rigor en Rutas**: Usar siempre rutas absolutas.
