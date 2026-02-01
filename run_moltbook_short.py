import os
import sys
import django
import time

# Configurar entorno Django
sys.path.append(r'c:\dell inspiron 15 3000\curso IA\aivideogen3')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aivideogen.settings')
django.setup()

from aivideogen.generator.models import Project
from aivideogen.generator.video_engine import generate_video_avgl

def run_test():
    # Buscar o crear el proyecto de prueba
    project_title = "Short Moltbook v8.6.2"
    project, created = Project.objects.get_or_create(
        title=project_title,
        defaults={
            'aspect_ratio': 'portrait',
            'status': 'pending'
        }
    )
    
    # Ruta al guion
    script_path = r'c:\dell inspiron 15 3000\curso IA\aivideogen3\aivideogen\guiones\moltbook_short.json'
    
    # Sobrescribir el script del proyecto con el contenido del JSON
    with open(script_path, 'r', encoding='utf-8') as f:
        project.script_content = f.read()
    
    project.status = 'pending'
    project.save()
    
    print(f"[*] Iniciando renderizado de: {project.title}")
    start = time.time()
    
    try:
        output = generate_video_avgl(project)
        end = time.time()
        print(f"[SUCCESS] Video generado en {end - start:.2f}s")
        print(f"[PATH] {output}")
    except Exception as e:
        print(f"[ERROR] Falló el renderizado: {e}")

if __name__ == "__main__":
    run_test()
