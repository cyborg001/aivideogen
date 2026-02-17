# Cómo Contribuir a AIVideogen

¡Gracias por tu interés en mejorar este motor de video con IA! Buscamos construir la herramienta open source más potente para creadores de contenido automatizado.

## 🐛 Reportar Bugs

Si encuentras un error, por favor abre un **Issue** con:
1.  **Título descriptivo**.
2.  **Pasos para reproducir**: Incluye el script AVGL o JSON que causó el fallo.
3.  **Logs**: Copia el output de la consola o adjunta el archivo `debug_output.txt`.
4.  **Entorno**: Sistema Operativo y versión de Python.

## 💡 Sugerir Funcionalidades

¿Tienes una idea genial? Abre un Issue con la etiqueta `enhancement` y describe:
- Qué problema resuelve tu idea.
- Cómo te imaginas que funcionaría la nueva feature (ej. sintaxis `[AVATAR:ID]`).

## 🛠️ Desarrollo

1.  **Haz un Fork** del repositorio.
2.  **Crea una Rama** para tu cambio:
    ```bash
    git checkout -b fix/mi-arreglo
    # O para nuevas funciones:
    git checkout -b feat/mi-nueva-funcion
    ```
3.  **Estilo de Código**: Intentamos seguir PEP 8, pero priorizamos la legibilidad. Usa nombres de variables descriptivos en español o inglés (consistente con el archivo que editas).
4.  **Tests**: Si añades una función compleja, intenta incluir un test unitario en `tests/`.

## 📦 Pull Requests

- Asegúrate de que tu código pasa los tests existentes.
- Describe tus cambios en la descripción del PR.
- Si tu cambio afecta a la documentación (`README.md` o manuales), actualízala también.

## 📜 Código de Conducta

Sé respetuoso con otros contribuidores. Cualquier comportamiento de acoso o falta de respeto resultará en un bloqueo permanente del proyecto.

¡Gracias por ayudar a democratizar la creación de video con IA! 🚀
