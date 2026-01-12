import os
import sys
import time
import django
from django.conf import settings

# 1. Setup Django Environment (Now from inside web_app)
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from generator.models import VideoProject
from generator.utils import generate_video_process

def run_benchmark():
    print("🚀 INICIANDO BENCHMARK DE RENDIMIENTO (v2.22.0) 🚀")
    print("--------------------------------------------------")
    
    # Correct path to script (it's in noticias/aeroespacial relative to web_app root)
    script_path = os.path.join(os.path.dirname(__file__), 'noticias', 'aeroespacial', 'guion_aeroespacial_2026.md')
    if not os.path.exists(script_path):
        # Alternative path check
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'web_app', 'noticias', 'aeroespacial', 'guion_aeroespacial_2026.md'))

    with open(script_path, 'r', encoding='utf-8') as f:
        script_text = f.read()

    # Create a temporary project for benchmarking
    project = VideoProject.objects.create(
        title="BENCHMARK PERFORMANCE 2026",
        script_text=script_text,
        status='pending',
        engine='edge',
        voice_id='es-ES-AlvaroNeural'
    )
    
    print(f"🎬 Proyecto creado: {project.title}")
    print(f"📦 Rama actual: feature/performance-evolution-qsv")
    print(f"⚙️ Configuración: Audio Paralelo + Intel QSV + Asset Cache")
    print("--------------------------------------------------")

    start_time = time.time()
    
    # Run the generator
    generate_video_process(project)
    
    end_time = time.time()
    total_duration = end_time - start_time
    
    project.refresh_from_db()
    
    print("--------------------------------------------------")
    if project.status == 'completed':
        print(f"✅ BENCHMARK COMPLETADO CON ÉXITO")
        print(f"⏱️ Tiempo Total: {int(total_duration)} segundos")
        print(f"🎥 Video Generado: {project.output_video.name}")
        
        # Check if QSV was used
        if project.log_output and "Intel QuickSync (QSV)" in project.log_output:
            print("🏎️ Hardware Acceleration: Intel QSV [ACTIVE]")
        else:
            print("⚠️ Hardware Acceleration: CPU Fallback [USED]")
            
        if project.log_output and "audios generados en paralelo" in project.log_output:
            print("🎙️ Parallel Audio: [ACTIVE]")
    else:
        print(f"❌ BENCHMARK FALLIDO: {project.status}")
        print(f"📝 Logs:\n{project.log_output}")

    # project.delete()

if __name__ == "__main__":
    run_benchmark()
