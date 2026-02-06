import os
import sys
import django
import json
import time
from pathlib import Path

# Configurar rutas relativas al proyecto
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent # aivideogen/aivideogen

sys.path.append(str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import VideoProject
from generator.video_engine import generate_video_avgl

def run_turbo_test():
    print("STARTING PERFORMANCE TEST: TURBO MODE (v10.0-BETA)")
    print("-" * 60)
    
    # 1. Crear un guion con múltiples escenas para notar el paralelismo
    test_script = {
        "title": "Turbo Test Bill",
        "voice": "es-ES-AlvaroNeural",
        "blocks": [
            {
                "title": "Bloque de Velocidad",
                "scenes": [
                    {
                        "title": f"Escena {i+1}",
                        "text": f"Esta es la escena numero {i+1} procesada en paralelo para validar el modo turbo.",
                        "assets": [{"type": "floating_ai_robot.png", "zoom": "1.0:1.1"}]
                    } for i in range(4) # 4 escenas para probar con 4 núcleos
                ]
            }
        ]
    }
    
    # 2. Crear proyecto con 4 trabajadores (Modo Turbo)
    project = VideoProject.objects.create(
        title="Turbo Test Performance",
        script_text=json.dumps(test_script, indent=2),
        aspect_ratio="landscape",
        status="pending",
        render_mode="cpu",
        render_workers=4  # <--- ACTIVANDO MODO TURBO
    )
    
    print(f"[*] Proyecto ID: {project.id}")
    print(f"[*] Trabajadores asignados: {project.render_workers}")
    print(f"[*] Iniciando renderizado paralelo...")
    
    try:
        start_time = time.time()
        output_path = generate_video_avgl(project)
        end_time = time.time()
        
        print(f"\n[SUCCESS] Modo Turbo validado con exito!")
        print(f"Path: {output_path}")
        print(f"Total Time: {end_time - start_time:.2f} seconds")
        
        # Guardar resultados para análisis
        project.refresh_from_db()
        if project.status == 'completed':
            print(f"Final Status in DB: {project.status}")
            
    except Exception as e:
        print(f"\n[ERROR] Error en el Modo Turbo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # Importante: En Windows, ProcessPoolExecutor requiere este guard
    run_turbo_test()
