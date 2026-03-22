---
description: Protocolo para la ejecución autónoma de misiones enviadas por email.
---

Este workflow permite a Bill operar con mayor autonomía en misiones marcadas como seguras o de análisis, minimizando la necesidad de permisos manuales.

// turbo-all
1. Leer las instrucciones de la misión en `inbox/mission_*.md`.
2. Identificar si la misión requiere análisis de archivos locales (PDF, JSON, TXT).
3. Utilizar herramientas de lectura directa (`view_file`, `grep_search`) que no requieren aprobación manual constante.
4. Generar el reporte o análisis en un archivo temporal en `/tmp/`.
5. Enviar el resultado automáticamente al Arquitecto mediante el sistema de respuesta de Bill Bridge.

> [!IMPORTANT]
> Las acciones destructivas (borrar carpetas, modificar código fuente o subir a producción) seguirán requiriendo aprobación manual obligatoria por seguridad del Arquitecto.
