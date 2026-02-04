# 🗂️ Dashboard Global de Proyectos

Este documento es nuestra central de mando. Aquí rastreamos el progreso de cada pilar del proyecto y las tareas pendientes.

---

## 🚀 1. Software: AI Video Generator (v8.7.0)
**Estado:** Estable / Producción
**Objetivo:** Mantener y evolucionar el motor de creación de video.

- [x] Parche agresivo de sockets e hilos para evitar cuelgues de música.
- [x] Implementar sistema de Overlays cinematográficos.
- [x] Añadir control de velocidad de voz (`EDGE_RATE`).
- [x] Corregir visibilidad de `.env.example` en distribución.
- [ ] **TODO:** Permitir que el guion de ejemplo se lea desde un archivo `.txt` externo.
- [ ] **TODO:** Investigar la aplicación de Ken Burns a archivos MP4 (actualmente solo estático).
- [ ] **TODO:** Refinar la UI para mostrar una previsualización de overlays antes de generar.

---

## 🎬 2. Contenido: Hitos 2026-2027 (Video 7 min)
**Estado:** Fase de Producción Final
**Objetivo:** Crear un documental épico sobre el futuro próximo de la ciencia.

- [x] Investigación y redacción del guion de 7 minutos.
- [x] Mapeo de assets y generación de prompts visuales.
- [x] Primera prueba de renderizado exitosa.
- [ ] **TODO:** Generar el lote final de 5 imágenes de soporte faltantes.
- [ ] **TODO:** Realizar render final en v2.17.6 usando Overlays de "polvo" y "luz".
- [ ] **TODO:** Revisar la sincronización de las pausas dramáticas con los hitos clave.

---

## ✍️ 3. Literatura: "El Velo Gravitacional"
**Estado:** Edición y Lore (Hard Sci-Fi)
**Objetivo:** Escribir una novela de ciencia ficción rigurosa y culturalmente rica.

- [x] Refinar Capítulos 1 al 6 con conceptos de Relatividad General.
- [x] Actualizar la "Biblia del Universo" con el efecto Geodésica.
- [x] Integrar jerga caribeña auténtica en los diálogos de Nathan.
- [ ] **TODO:** Estimar tiempo de lectura total y conteo de palabras del manuscrito completo.
- [ ] **TODO:** Revisar la coherencia de los géneros de los personajes secundarios.
- [ ] **TODO:** Expandir el trasfondo del "Distrito RD" y las consecuencias de la Gran Inundación.

---

## 💡 4. Serie: "Sabías Que?" (Shorts)
**Estado:** Planeación e Ideación
**Objetivo:** Crear una serie de videos cortos (30-60s) sobre descubrimientos accidentales.

- [x] Crear carpeta de proyecto `noticias/proyecto_sabias_que`.
- [x] Definir lista inicial de 6 descubrimientos.
- [x] Redactar los 6 guiones en formato de 5 columnas en `guiones_pro_v1.md`.
- [/] **TODO:** Generar assets visuales temáticos para cada caso.
    - [x] Guía de estilo "Moderno no-futurista" lista en `prompts_visuales.md`.
    - [x] Imágenes Casos 1, 2, 3 y 4 listas en `media/assets`.
    - [ ] Casos 5 y 6 pendientes (Esperando reinicio de cuota de IA).

---

## 🛠️ Herramientas de Apoyo
- **Script de conteo**: `count_lines.py` (Funcional).
- **Manuales**: `GUIA_DE_EFECTOS.md`, `MANUAL_COMPLETO.md`.

---
*¿Deseas que continuemos con alguna de estas tareas o prefieres abrir un nuevo frente de trabajo?*
