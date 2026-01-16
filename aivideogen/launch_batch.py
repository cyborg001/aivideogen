import os
import django
import sys
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import VideoProject
from generator.utils import generate_video_process
from django.conf import settings

projects_to_launch = [
    {
        "title": "Artemis II: Regreso a la Luna",
        "script_path": r"c:\Users\Usuario\Documents\curso creacion contenido con ia\noticias\2026_del_1-12\artemis_ii.json",
        "aspect_ratio": "portrait"
    },
    # {
    #     "title": "NotIACi: Resumen Quincenal Enero 2026",
    #     "script_path": r"c:\Users\Usuario\Documents\curso creacion contenido con ia\noticias\2026_del_1-12\resumen_quincenal_horizontal.json",
    #     "aspect_ratio": "landscape"
    # }
]

print("📊 --- INICIANDO PROCESAMIENTO POR LOTES (SEQUENTIAL MODE) ---")

for p_data in projects_to_launch:
    print(f"\n🎬 PROYECTO: {p_data['title']}")
    
    # 1. Read script
    try:
        with open(p_data['script_path'], 'r', encoding='utf-8') as f:
            script_content = f.read()
    except Exception as e:
        print(f"❌ Error leyendo guion en {p_data['script_path']}: {e}")
        continue

    # 2. Create database entry
    project = VideoProject.objects.create(
        title=p_data['title'],
        script_text=script_content,
        aspect_ratio=p_data['aspect_ratio'],
        auto_upload_youtube=True,
        engine='edge',  # Engine will use script JSON for specific voice
        status='pending'
    )
    
    print(f"⚙️  Renderizando... (ID: {project.id})")
    
    # 3. Execute generation (Sync call ensures sequential processing)
    try:
        generate_video_process(project)
    except Exception as e:
        print(f"❌ Error fatal en la generación de {p_data['title']}: {e}")
        project.status = 'error'
        project.log_output += f"\n[Script] ERROR FATAL: {str(e)}"
        project.save()
        continue
    
    # 4. Final check
    project.refresh_from_db()
    if project.status == 'completed':
        print(f"✅ ÉXITO: {project.title}")
        if project.youtube_video_id:
            print(f"📺 YOUTUBE: https://www.youtube.com/watch?v={project.youtube_video_id}")
        else:
            print("⚠️ El video se generó pero hubo un problema en la subida automática.")
    else:
        print(f"❌ FALLÓ: {project.title} (Status: {project.status})")

print("\n✨ --- LOTE FINALIZADO ---")
