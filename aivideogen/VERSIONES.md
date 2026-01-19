# Registro de Versiones - AIVideogen (v3.x)

Este archivo registra la evolución del motor de eventos **AVGL**.

| Versión | Fecha | Hito Técnico | Cambios Realizados |
| :--- | :--- | :--- | :--- |
| **3.0.0** | 2026-01-16 | **Unified Engine Era** | **Legacy Removed:** Eliminación total del motor antiguo. Todo el renderizado pasa por AVGL v4. <br> **Smart Text Bridge:** Soporte nativo de `FIT`, `ZOOM`, `OVERLAY` en guiones de texto (5 columnas) mediante conversión automática a JSON. <br> **Single Pipeline:** Unificación de lógica de renderizado para máxima consistencia. |
| 2.24.4 | 2026-01-11 | **Smart Title Cleaner** | Mejora de limpieza de títulos con Regex (Strips emojis & prefixes). |
| 2.0.0 | 2025-12-27 | Lanzamiento Dist | Creación de la versión independiente (dist) con sistema de migraciones automáticas. |
| 2.1.0 | 2025-12-28 | IA Scripting | Integración de Gemini Pro para generación automática de guiones y prompts visuales. |
| 2.2.0 | 2026-01-01 | **Professional Finish Update** | **Ken Burns Granular:** Control de dirección desde el guion. <br> **Audio Ducking:** Atenuación automática de música. <br> **Visual Asset:** Video CTA animado integrado. |
| 2.2.1 | 2026-01-01 | **Audio Ducking Hotfix** | Solución a error `unsupported operand type`. |
| 2.2.2 | 2026-01-01 | **Numpy Vectorization Fix** | Soporte para procesamiento de arreglos en Ducking. |
| 2.2.3 | 2026-01-01 | **Title Integrity Shield** | Blindaje del modelo para evitar sobrescritura de títulos. |
| 2.2.5 | 2026-01-01 | **Audio Stereo Fix** | Soporte para broadcasting en audio estéreo (2 canales). |
| 2.3.0 | 2026-01-01 | **Silent Breaks & UX** | Soporte para etiqueta `[PAUSA:segundos]` en el guion. |
| 2.4.0 | 2026-01-01 | **Professional Finish & Fades** | **Audio Fades:** Suavizado de 0.2s en transiciones (sin ruidos). <br> **UI Guide:** Ejemplos maestros de DIR y PAUSA en la interfaz. |
| 2.5.0 | 2026-01-01 | **UI Simplification** | Eliminación del checkbox redundante "Activar Desplazamiento Dinámico". Ahora el efecto Ken Burns se activa exclusivamente mediante el guion (`DIR`). |
| 2.6.0 | 2026-01-01 | **Strategic Scripting** | Aplicación de la **Ley del Gancho** y **Conclusión Profunda** en guiones. Integración de pausas rítmicas para maximizar el Audio Ducking. |
| 2.8.0 | 2026-01-01 | **Advanced Ken Burns** | Control quirúrgico del encuadre mediante porcentajes (`DIR:START:END`). Permite sub-movimientos precisos en cualquier dirección. |
| 2.9.0 | 2026-01-01 | **Pro Standalone Sync** | Independización total del repositorio, nuevo README profesional y descripción de alto nivel para GitHub. |
| 2.9.4 | 2026-01-01 | **AI Scripting Pro** | Actualización del cerebro IA (Gemini) para generar guiones en formato de 4 columnas, con control de Ken Burns y pausas rítmicas automáticas. |
| 2.9.5 | 2026-01-01 | **Pause Hotfix** | Corrección de error crítico en `AudioClip` para compatibilidad con MoviePy 2.0. |
| 2.9.6 | 2026-01-01 | **Steady Render & Robust Parser** | Generación de silencios en memoria (Stereo) para evitar OSErrors. Limpieza inteligente de nombres de archivo y soporte total para Ken Burns avanzado en el parser. |
| 2.9.8 | 2026-01-01 | **Human-Centric Gemini Fix** | Migración al endpoint estable `v1` y modelo `gemini-1.5-flash-latest`. Implementación de mensajes de error "humanizados". |
| 2.9.9 | 2026-01-01 | **Actionable Error System** | Refinamiento de mensajes de error de IA para guiar al usuario en la resolución de problemas (API Keys, conexión, config). |
| 2.10.0 | 2026-01-01 | **Gemini 2.5 Flash Upgrade** | Migración al modelo `gemini-2.5-flash` (2026) tras diagnóstico exhaustivo de la API. Corrección definitiva del error 404. |
| 2.10.1 | 2026-01-01 | **Gemini 2.5 Compatibility Fix** | Eliminación de `response_mime_type` no soportado. Parsing robusto de JSON desde respuestas de texto de Gemini 2.5. |
| 2.10.2 | 2026-01-01 | **Smart Word Counter** | Corrección del timing de actualización del contador de palabras para que funcione correctamente con guiones generados por IA. |
| 2.10.3 | 2026-01-01 | **UI Label Update** | Actualización del label del editor de guiones para reflejar el formato PRO de 4 columnas con guía rápida. |
| 2.11.0 | 2026-01-02 | **Smart Categories & Pro Docs** | **Auto-Categories:** Sistema de gestión inteligente de categorías. <br> **Deep Clean:** Paquete libre de archivos temporales y con ejemplos mínimos. <br> **Pro Docs:** Manual completo y guías integradas en el paquete. |
| 2.11.1 | 2026-01-02 | **Ken Burns Docs Fix & Template Repair** | **Docs Update:** Documentación actualizada con formato avanzado `DIR:START:END`. <br> **UI Guide:** Texto de ayuda en `/create` actualizado con ejemplos de porcentajes. <br> **Template Fix:** Corrección crítica del TemplateSyntaxError en AI Hub. |
| 2.12.0 | 2026-01-03 | **Revolutionary Effects System** | **HOR/VER System:** Reemplazo completo de DER/IZQ/ARR/ABA por sistema simplificado de 2 ejes (HOR/VER). <br> **Real ZOOM:** Implementación de ZOOM_IN/ZOOM_OUT con zoom real, no simulado. <br> **Diagonal Support:** Soporte completo para movimientos diagonales (HOR+VER). <br> **Triple Effects:** Combinaciones HOR+VER+ZOOM funcionando perfectamente. <br> **Cartesian System:** Lógica vertical invertida (VER:0=abajo, VER:100=arriba). <br> **Upload Fix:** Límites de carga aumentados a 1000 archivos/100MB. |
| 2.12.1 | 2026-01-04 | **Media & UI Stability Hub** | **Single Playback:** Control inteligente de audio para evitar bloqueos del servidor. <br> **Duplicate Shield:** Prevención de archivos duplicados en Música y Assets. <br> **Buffer Optimization:** Carga bajo demanda (`preload="none"`) para ahorro de RAM. <br> **UI Rendering Fix:** Corrección de visualización de fechas en el Hub de Audio. |
| 2.13.0 | 2026-01-05 | **Pro Kinetic & Engine Upgrade** | **Unified Ken Burns:** Movimientos HOR/VER independientes de orden y sintaxis simplificada `ZOOM:S:E`. <br> **Kinetic Fix:** Solución a error de escala incremental y anclaje dinámico de posición. <br> **TTS Speed Control:** Soporte para variable `EDGE_RATE` en `.env` (+15% por defecto). <br> **Media Safety:** Garantía de cobertura total (Cover) en renderizado de assets. |
| 2.14.0 | 2026-01-05 | **Smart Progress & Timing** | **Pre-Render Estimator:** Cálculo dinámico de la duración del video antes de empezar. <br> **Processing Estimator:** Cálculo del tiempo de renderizado esperado según la duración. <br> **Scene Progress:** Barra de progreso textual `[Escena X/Y]` con porcentajes en tiempo real. <br> **Engine Resilience:** Validación profunda de sintaxis y assets previa al inicio. |
| 2.15.0 | 2026-01-05 | **Smart Fallback & Resilience** | **Non-Blocking Validation:** Los archivos faltantes ahora son advertencias, no errores. <br> **Automatic Fallback:** Si una imagen no existe, el sistema elige una aleatoria de `assets` automáticamente. <br> **Fail-Safe Rendering:** El proceso garantiza la finalización del video incluso con assets huérfanos. |
| 2.15.2 | 2026-01-05 | **Precision Timing & Logs** | **Real-Time Stopwatch:** El sistema mide y muestra el tiempo exacto consumido al finalizar el video. <br> **Estimation Logic:** Calibración de estimación (5x) para ser más realista con videos de larga duración y efectos visuales. <br> **Zero-Time Fix:** Corrección de visualización para videos cortos (ahora muestra segundos). |
| 2.16.0 | 2026-01-05 | **Timing Precision Upgrade** | Ajuste de sobrecoste base por escena (15s) para precisión total en la estimación de tiempo. |
| 2.17.0 | 2026-01-05 | **Cinematic Overlays System** | Soporte para capas de polvo, grano y luces mediante la instrucción `OVERLAY:nombre` en el guion. |
| 2.18.1 | 2026-01-06 | **Music Sync & Socket Fix** | **Socket Release:** Parche agresivo de liberación de sockets en el reproductor de música para evitar bloqueos del servidor. <br> **Threaded Log Fix:** Corrección del comando de arranque y actualización global de versión. |
| 2.18.2 | 2026-01-07 | **Granular Overlay Volume** | **Tactical Control:** Control de volumen granular para Overlays (`OVERLAY:nombre:N`) en escala 0-4. <br> **CTA Sync:** Inclusión de asset `suscribete.mp4` y mensaje estándar en guiones. |
| 2.19.0 | 2026-01-07 | **Process Control & UX** | **Render Cancellation:** Opción de detener la generación de video en tiempo real desde la UI. <br> **Form Persistence:** El formulario de creación ahora recuerda los datos automáticamente mediante LocalStorage. |
| 2.19.1 | 2026-01-07 | **Robustness & Fixes** | **Parser Robustness:** Soporte para guiones con columnas extra (ignorancia inteligente). <br> **TTS Protection:** Evita archivos corruptos ante textos vacíos o comandos de efectos solos. |
| 2.19.2 | 2026-01-07 | **Overlay Audio Control** | **Silent by Default:** Los Overlays (grain, dust, etc.) ahora son silenciosos por defecto a menos que se especifique volumen (`OVERLAY:nombre:1-4`). |
| 2.19.3 | 2026-01-07 | **Mixed Pauses Support** | **Audio Logic Refactor:** Soporte para voz y pausas (`[PAUSA:X]`) en la misma escena mediante concatenación dinámica. Ducking corregido para subir música solo en silencios. |
| 2.19.4 | 2026-01-07 | **Dedicated Pause Format** | **Official Standard:** Pausas estandarizadas en líneas dedicadas para mayor estabilidad. Corrige lectura accidental de etiquetas por el motor TTS. |
| 2.20.0 | 2026-01-07 | **Optional PAUSA Column** | **5-Column Format:** Nueva columna opcional PAUSA para pausas más limpias (`TITULO \| IMAGEN \| EFECTO \| TEXTO \| PAUSA`). <br> **Backward Compatible:** Soporte completo para formato antiguo de 4 columnas. <br> **Cinematic Continuity:** Efectos visuales continúan durante pausas. <br> **AI Integration:** Generación automática con 5 columnas. |
| 2.21.5 | 2026-01-08 | **Smart Slack Engine** | Optimización de encuadre Ken Burns. Evita el "over-zoom" en cambios de orientación (ideal para cohetes y edificios). |
| 2.21.4 | 2026-01-08 | **Time Prediction Fix** | Recalibración del motor de estimación de tiempo de renderizado (ahora mucho más preciso). |
| 2.22.1 | 2026-01-09 | **Consolidated Performance Engine** | **Parallel Audio Generation:** Inicio de generación casi instantáneo mediante `asyncio.gather`. <br> **Manual Overlay Volume:** Control preciso de volumen para Overlays (`OVERLAY:nombre:vol`). <br> **Standard CPU Render:** Retorno a renderizado por CPU optimizado (superfast) para máxima estabilidad y compatibilidad. <br> **Retry Correction:** Botón de "Reintentar" restaurado para proyectos fallidos y analíticas fix. |
| 2.23.0 | 2026-01-11 | **Infographic Integrity Engine** | **FIT Mode:** Implementación del comando `FIT` para visualización íntegra de imágenes con AR no estándar. <br> **Safe Zoom:** Algoritmo para prevenir recortes de píxeles en infografías técnicas. <br> **Audit:** Barrido completo del guion maestro para proteger datos críticos. |
| 2.24.0 | 2026-01-11 | **Auto-YouTube Integration** | **Auto-Upload:** Nueva opción para subir automáticamente a YouTube tras el render. <br> **Quick Access:** Botón directo de YouTube en la lista de proyectos. <br> **Unified Description:** Motor centralizado de generación de descripciones pro. |

---
| 2.25.0 | 2026-01-15 | **Robust Audio & Asset Shield** | **Dynamic Volume:** Control de volumen de música por bloque (ej. silencio dramático). <br> **Asset Shield:** Normalización automática de nombres de assets (arranque seguro ante timestamps). <br> **SFX Precision:** Control de volumen granular para efectos de sonido. |
| 2.26.0 | 2026-01-16 | **Strategic Logic Relocation** | **Smart Logic Shift:** Lógica de "Zoom Continuo" movida del guion (`convert_script.py`) para control absoluto. <br> **Aggressive Ducking:** Audio Ducking re-calibrado al 5% (casi nulo). <br> **Neutral Voice Strategy:** Adopción de voces neutrales (`es-US-Alonso`) para narración. |
| 2.26.1 | 2026-01-17 | **Stability & Workflow Patch** | **Manual Processing:** Inicio manual de generación para control total. <br> **Clean Lifecycle:** Eliminación limpia de proyectos y archivos huérfanos. <br> **Critical Engine Fix:** Validación de tipos de Assets (evita fallos NoneType) y manejo de errores robusto en V4. |

---
*Actualizado al 17-01-2026*
