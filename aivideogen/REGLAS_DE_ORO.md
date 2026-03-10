# 📑 Reglas de Oro - NotiACI

Este documento contiene las reglas fundamentales de identidad y operación para el proyecto NotiACI. Estas reglas deben seguirse estrictamente en cada generación.

## 👤 Identidad y Marca
- **Saludo Oficial**: En videos largos y descripciones, el saludo debe ser: **"¡Hola! Bienvenidos a mi canal"**. En **Shorts/TikTok**, se omite el saludo para ir directo al grano.
- **Tono**: Profesional, proactivo y preciso.
- **Audiencia**: Arquitectos de contenido y entusiastas de la IA y ciencia.

## 🎬 Estrategia de Contenido (Hook-First)
1. **El Gancho (0-2s)**: Impacto directo con la noticia.
2. **Identidad**: En videos largos, el saludo de marca viene inmediatamente después del gancho inicial. En **Shorts**, la identidad se transmite por el ritmo y los assets.
3. **Ritmo Visual**: Cambio de escenas cada 2-4 segundos.
4. **Cierre**: Pregunta provocadora para fomentar comentarios y suscripción.

## 🎨 Estándares Visuales
1. **Encuadre Completo**: Las imágenes deben **completar el cuadro** (Full-frame). Evitar bordes blancos, letterboxing o composiciones incompletas.
2. **Estilo**: Uso de "Epic graphic novel art" o "Cinematic concept art" para mantener la atmósfera épica.
3. **Composición**: Priorizar formatos panorámicos y composiciones cinematográficas que llenen el área de visión.

## 🛠️ Protocolos Operativos
- **Planificación Primero**: Nunca realizar ediciones sin presentar un plan aprobado.
- **Sintaxis de Etiquetas AVGL**: Las etiquetas (ej: `[PHO:h]`, `[TENSO]`) siempre se cierran de forma simple, sin repetir parámetros (ej: `[/PHO]`, `[/TENSO]`). Nunca usar cierres como `[/PHO:h]`.
- **Ramas de Desarrollo**: Los cambios que impliquen modificaciones del código siempre deben realizarse en una **nueva rama**.
- **Cero Suposiciones**: Ante dudas sobre rutas o intención, preguntar al Arquitecto.
- **Puntuación Natural**: Evitar el uso de etiquetas `[PAUSA]`. Confiar en las comas y puntos para dictar el ritmo del TTS, ya que el motor los interpreta correctamente.
- **Verificación Sistemática**: Probar cambios y documentar resultados.
- **Rigor en Rutas**: Usar siempre rutas absolutas.
