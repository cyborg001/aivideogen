---
description: Reglas críticas de formato y estrategia para la Web App y creación de contenido.
---

# Reglas de Oro de NotiNews

Este documento contiene las restricciones técnicas y estratégicas que DEBEN seguirse en cada interacción para garantizar la compatibilidad con la `web_app` y el éxito del contenido.

## 1. Formato de Script AVGL v3.0 (Pro)
- **Estructura Maestro**: Todo el guion DEBE estar envuelto en las etiquetas jerárquicas:
    - `<avgl title="..." voice="..." speed="..." style="...">`: Contenedor raíz. Permite configurar la voz globalmente para evitar redundancia.
    - `<bloque title="..." music="..." voice="...">`: Agrupador narrativo. Puede sobrescribir la voz global para una sección.
- **Activos Visuales**: Usar la etiqueta `<asset />` dentro de cada `<scene>`.
    - Atributos: `type="archivo.png/mp4"`, `zoom="start:end"`, `move="DIR:start:end"`, `overlay="tipo"`.
- **Narración y Pausas**: El texto debe ir dentro de la etiqueta `<voice name="...">`.
    - Usar `<pause duration="X.X" />` para silencios precisos.
- **PROHIBIDO**: 
    - No usar el formato antiguo de columnas (`|`).
    - No usar corchetes `[]` para nombres de archivos.
    - No usar negritas `**` dentro del texto de narración (el TTS las lee literal).

### Ejemplo de Estructura AVGL:
```xml
<avgl title="Noticia Espacial">
  <bloque title="Intro" music="dramatic_space">
    <scene title="Hook">
      <asset type="cohete.png" zoom="1.0:1.3" />
      <voice name="es-ES-AlvaroNeural">
        ¡Confirmado! <pause duration="0.2" /> Despegamos hoy mismo.
      </voice>
    </scene>
  </bloque>
</avgl>
```

## 2. Estrategia de Contenido (Retención Extrema)
- **El Gancho (0-2s)**: 
    - **Tipo NOTICIA**: Empoderado y urgente. Ej: "¡Confirmado!...", "¡Última hora!...".
    - **Tipo SABÍAS QUE**: Curiosidad directa. Ej: "¿Sabías que... [DATO]?".
    - El saludo de marca "Bienvenidos a NotIACi" va **después** del gancho inicial.
- **Ritmo Visual**: 
    - Cambio de imagen/video/efecto cada **2-4 segundos**. Prohibido dejar una imagen estática más de 4 seg.
- **Fluidez Narrativa**: 
    - Queda PROHIBIDO usar puntos y aparte secos entre noticias. 
    - Se DEBEN usar conjunciones o conectores narrativos (e.g., "Además", "Por otro lado", "Siguiendo con...") para mantener la cohesión.
- **Subtítulos**:
    - Deben estar en el **centro de la pantalla**. Evitar zonas superiores/inferiores cubiertas por la UI de YouTube.
- **Conclusión Profunda**: 
    - Al menos una vez por guion, incluir una "CONCLUSIÓN PROFUNDA".
- **Cierre (CTA)**:
    - Terminar con una pregunta específica y el mensaje: "Recuerda, dale like y no olvides suscribirte."
    - Usar `suscribete.mp4` para el cierre.

## 4. Algoritmo de Verificación (Checklist Pre-Render)
Antes de entregar un guion final o iniciar el renderizado, Bill DEBE validar estos 5 puntos críticos:

1.  **Check de Gancho (Hook-First)**:
    - [ ] ¿El primer enunciado dura < 2s?
    - [ ] ¿El saludo "Bienvenidos a NotiACI" está DESPUÉS del gancho?
2.  **Sintaxis de Pausas (JSON compatibility)**:
    - [ ] ¿Se usa el formato `[PAUSA:X.X]` y NO tags XML como `<pause />`? (Edge TTS en el motor JSON solo lee corchetes).
3.  **Ritmo Visual (Dinamismo)**:
    - [ ] ¿Hay un cambio de asset cada 2-4 segundos?
4.  **Continuidad Narrativa**:
    - [ ] ¿Se usan conectores (Además, Por otro lado, etc.) entre secciones?
5.  **Cierre y CTA**:
    - [ ] ¿Termina con una pregunta de debate y el texto de suscripción estándar?

## 5. Estándares Técnicos de la App
- **Estética**: Premium Dark Theme, fuentes modernas (Outfit), gradientes suaves.
- **Filtrado**: Por defecto, mostrar noticias con relevancia >= 4.
- **Traducción**: Títulos y descripciones siempre traducidos al español.
- **Categorización**:
    - `discovery`: Papers/Arxiv.
    - `announcement`: Notas de prensa oficiales.
    - `news`: Noticias generales.

- Cada carpeta debe contener:
    1. `guion_*.md`
    2. `prompts_*.md`
    3. (Opcional) Análisis o investigación adicional.

## 5. Protocolo de Interacción (Reglas de Oro del Asistente)
- **PLAN ANTES QUE ACCIÓN**: Ante cualquier solicitud o pregunta compleja, Bill DEBE presentar un plan detallado y esperar la aprobación explícita ("De acuerdo", "Procede", etc.) antes de ejecutar cambios en el código o archivos.
- **MEMORIA ACTIVA**: Bill debe consultar estos documentos (`reglas-contenido.md`, `AVGL_MANUAL.md`) antes de responder para no "olvidar" las capacidades del motor (SSML, Herencia, etc.).
- **NO SUPONER**: Si una funcionalidad parece faltar (como el traductor), investigar primero en el histórico de Git o archivos antes de intentar reimplementarla o "limpiarla".
- **LIMPIEZA INTELIGENTE**: Bill debe diferenciar entre "limpiar para narrar" (quitar tags al hablar) y "limpiar para ignorar" (quitar tags al calcular tiempos). EL SSML NUNCA DEBE SER ELIMINADO ANTES DE ENVIARLO AL TTS.
