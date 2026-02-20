
import os
import sys
import django
import json
from pathlib import Path

# Setup Project Environment
base_dir = Path(__file__).resolve().parent
sys.path.append(str(base_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import VideoProject
from generator.video_engine import generate_video_avgl

def render_short():
    print("--- Iniciando renderizado del Short Cientifico ---")
    
    json_path = base_dir / 'guiones' / 'noticias' / 'ciencia_ia_feb2026' / 'noticia_ia_ciencia_feb2026.avgl.json'
    
    if not json_path.exists():
        print(f"Error: No se encuentra el archivo en {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        script_data = json.load(f)
        
    script_text = json.dumps(script_data, indent=4)
    title = f"Short: {script_data.get('title', 'Noticia Ciencia')}"

    # Create project in DB
    project, created = VideoProject.objects.get_or_create(
        title=title,
        defaults={
            'script_text': script_text,
            'aspect_ratio': 'portrait', # Corto = Short/Portrait
            'engine': 'edge'
        }
    )
    
    # Update project state for clean render
    project.script_text = script_text
    project.aspect_ratio = 'portrait'
    project.status = 'queued'
    project.save()
    
    print(f"Proyecto ID: {project.id} - '{project.title}'")
    print("Renderizando... (Esto puede tomar unos minutos)")
    
    try:
        generate_video_avgl(project)
        
        if project.output_video:
            print(f"EXITO! Video generado en: {project.output_video.path}")
        else:
            print("El renderizado termino pero no se encontro el archivo de salida.")
    except Exception as e:
        print(f"Error durante el renderizado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    render_short()
