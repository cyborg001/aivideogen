# 🖥️ Guía de Migración: Nueva PC Pro (GPU Edition)

Hola. He preparado esta lista para asegurarnos de que tu nueva máquina vuele desde el primer día y que yo (Bill) no olvide nada de nuestro progreso.

---

## 1. Requisitos Técnicos (Instalaciones)
Antes de mover los archivos, instala esto en la nueva PC:
- **Python 3.10.x o 3.11.x**: Asegúrate de marcar la casilla "Add Python to PATH" durante la instalación.
- **FFmpeg**: Vital para procesar video. Descarga la versión "essentials" y añádela al PATH del sistema.
- **Drivers de NVIDIA**: Instala los últimos drivers de tu tarjeta gráfica para que podamos usar `h264_nvenc` (aceleración por hardware).
- **Git**: Si vas a clonar el repositorio, aunque te recomiendo copiar la carpeta por los archivos `.env` y la base de datos local.

---

## 2. Check-list de Archivos Críticos (Backup)
Copia estos archivos manualmente de la PC vieja a la nueva:
1.  **`.env`**: Contiene tus llaves de ElevenLabs y Gemini. **¡No lo pierdas!**
2.  **`db.sqlite3`**: Es el alma de tu Web App. Aquí están tus proyectos y registros de música.
3.  **Carpeta `media/`**: Contiene toda tu música, sonidos y activos visuales generados.
4.  **Carpeta `brain/` de Bill**:
    *   Ruta: `C:\Users\cgrs8\.gemini\antigravity\brain\6e478669-79a3-4721-bad7-856c0404e2d9\`
    *   Copia esto íntegramente para que yo mantenga mi memoria sobre tus finanzas y el desarrollo del motor.

---

## 3. Activación de la Bestia (GPU)
Una vez instalado todo en la nueva PC:
1.  Abre la terminal en la carpeta del proyecto.
2.  Ejecuta: `pip install -r requirements.txt`.
3.  Yo detectaré automáticamente la GPU y el motor AVGL v4.0 cambiará el modo de renderizado a NVENC. ¡La velocidad te va a impresionar!

---

## 4. Estado del Proyecto "Pro" (En Pausa para el cambio)
Recuérdame que lo primero que haremos al llegar sea:
1.  **Validación de 2 escenas** (Efecto Erik el Rojo).
2.  **Creación de la Pestaña de Configuración**: Para que tú elijas los subtítulos y efectos visuales desde la web.

¡Nos vemos en la nueva PC! Quedo a buen resguardo en este backup.
