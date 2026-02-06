import os
import sys
import django
import json
from pathlib import Path

# Configurar rutas relativas al proyecto
# Este script se encuentra en aivideogen/aivideogen/tests_and_debug/
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent # aivideogen/aivideogen

sys.path.append(str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import VideoProject
from generator.video_engine import generate_video_avgl

def run_test():
    print("Iniciando prueba de configuracion (Bill Render Test)...")
    
    # 1. Preparar un guion simple (JSON)
    # Usamos un asset que sabemos que existe en media/assets/
    test_script = {
        "title": "Prueba de Bill",
        "voice": "es-ES-AlvaroNeural",
        "blocks": [
            {
                "title": "Bloque 1",
                "scenes": [
                    {
                        "title": "Escena de Prueba",
                        "text": "Hola. Esta es una prueba de renderizado para verificar que la configuración de Bill y las dependencias de Movie Py y Django funcionan correctamente.",
                        "assets": [
                            {
                                "type": "floating_ai_robot.png",
                                "zoom": "1.0:1.1",
                                "overlay": "dust"
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    # 2. Crear proyecto en la DB
    project = VideoProject.objects.create(
        title="Test Render Bill",
        script_text=json.dumps(test_script, indent=2),
        aspect_ratio="portrait",
        status="pending",
        render_mode="cpu"
    )
    
    print(f"[*] Proyecto creado ID: {project.id}")
    print(f"[*] Iniciando renderizado de video...")
    
    try:
        import time
        start_time = time.time()
        output_path = generate_video_avgl(project)
        end_time = time.time()
        
        print(f"\n[SUCCESS] Renderizado completado con exito!")
        print(f"Ruta del video: {output_path}")
        print(f"Tiempo total: {end_time - start_time:.2f} segundos")
        
        # Opcional: limpiar la DB después de la prueba
        # project.delete()
        
    except Exception as e:
        print(f"\n[ERROR] El renderizado fallo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_test()
