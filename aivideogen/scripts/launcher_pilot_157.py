import os
import django
import sys

# Setup Django Environment
sys.path.append(r"c:\Users\hp\aivideogen\aivideogen")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import VideoProject
from generator.utils import generate_video_process

def main():
    project_id = 157
    try:
        project = VideoProject.objects.get(id=project_id)
        print(f"[*] Iniciando renderizado para Proyecto {project_id}: {project.title}")
        
        # Ejecutar el proceso unificado
        generate_video_process(project)
        
        project.refresh_from_db()
        if project.status == 'completed':
            print(f"[+] ÉXITO: Renderizado completado.")
        else:
            print(f"[-] ERROR: El estado final es {project.status}")
            print(f"    Logs: {project.log_output[-500:]}")
            
    except Exception as e:
        print(f"[!] Error fatal en el lanzador: {e}")

if __name__ == "__main__":
    main()
