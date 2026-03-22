
import os
import sys
import django
import json
from pathlib import Path

# Setup Project Environment
import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

base_dir = Path(__file__).resolve().parent
sys.path.append(str(base_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import VideoProject
from generator.video_engine import generate_video_avgl

def render_sastre_volador():
    print("--- Iniciando renderizado del Sabías Qué?: El Sastre Volador ---")
    
    json_path = base_dir / 'guiones' / 'sabias_que_sastre_volador.json'
    
    if not json_path.exists():
        print(f"Error: No se encuentra el archivo en {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        script_data = json.load(f)
        
    script_text = json.dumps(script_data, indent=4)
    title = f"Sabías Qué?: {script_data.get('title', 'El Sastre Volador')}"

    # Create/Update project in DB
    project, created = VideoProject.objects.get_or_create(
        title=title,
        defaults={
            'script_text': script_text,
            'aspect_ratio': 'portrait',
            'engine': 'edge'
        }
    )
    
    # Force update state
    project.script_text = script_text
    project.aspect_ratio = 'portrait'
    project.status = 'queued'
    project.save()
    
    print(f"Proyecto ID: {project.id} - '{project.title}'")
    print("Renderizando... (Este proceso usa FFmpeg e IA de voz)")
    
    try:
        generate_video_avgl(project)
        
        if project.output_video:
            print(f"\nEXITO! Video generado en: {project.output_video.path}")
        else:
            print("\nAVISO: El renderizado termino pero no se encontro un archivo de salida registrado.")
    except Exception as e:
        print(f"\nERROR: Error katastrofico durante el renderizado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    render_sastre_volador()
