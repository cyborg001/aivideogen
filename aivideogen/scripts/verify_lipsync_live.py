
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['PYTHONUTF8'] = '1'
import io
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.append(os.getcwd())
django.setup()

from generator.models import VideoProject
from generator.video_engine import generate_video_avgl

def run_lipsync_test():
    print("[*] Iniciando Escenario de Prueba: Lip-Sync Local (DirectML)")
    
    # Crear un proyecto de prueba
    test_script = {
        "title": "Prueba LipSync Bill v9.0",
        "voice": "es-MX-JorgeNeural",
        "blocks": [
            {
                "title": "Bloque de Prueba",
                "scenes": [
                    {
                        "title": "Trump LipSync Test",
                        "text": "Hola Arquitecto. Esto es una prueba de sincronización labial ejecutada totalmente en tu GPU local. Sin APIs externas, sin costos adicionales. ¡El futuro es ahora!",
                        "assets": [{"id": "trump_groenlandia.mp4"}],
                        "lipsync": True
                    }
                ]
            }
        ]
    }
    
    project = VideoProject.objects.create(
        title="TEST_LIPSYNC_V95_DEBUG",
        script_text=json.dumps(test_script),
        aspect_ratio='landscape',
        render_mode='gpu',
        status='pending'
    )
    
    print(f"[+] Proyecto creado ID: {project.id}")
    
    try:
        generate_video_avgl(project)
        project.refresh_from_db()
        if project.status == 'completed' and project.output_video:
             print(f"[SUCCESS] Lip-Sync completado. Video en: {project.output_video.path}")
        else:
             print(f"[-] El proyecto terminó con estado: {project.status}")
    except Exception as e:
        print(f"[ERROR] Fallo en el renderizado de prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_lipsync_test()
