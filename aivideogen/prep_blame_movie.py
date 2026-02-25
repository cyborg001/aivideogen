import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from generator.models import VideoProject

# 4 Partes Renderizadas (Obtener rutas absolutas)
parts_ids = [92, 93, 94, 95]
projects = VideoProject.objects.filter(id__in=parts_ids).order_by('id')
parts_paths = [p.output_video.path for p in projects]

if len(parts_paths) < 4:
    print(f"Error: Solo se encontraron {len(parts_paths)} partes.")
    exit(1)

# Construir JSON AVGL de ensamblaje con rutas ABSOLUTAS
assemble_json = {
    "title": "BLAME! - El Abismo de Silicio (Documental Completo)",
    "voice": "es-ES-AlvaroNeural",
    "background_music": None,
    "music_volume": 0,
    "blocks": [
        {
            "title": "Documental Completo",
            "scenes": [
                {
                    "title": f"Parte {i+1}",
                    "audio": p,
                    "assets": [{"id": p, "video_volume": 0.0, "fit": True}],
                    "text": "",
                    "pause": 0
                } for i, p in enumerate(parts_paths)
            ]
        }
    ],
    "hashtags": ["BLAME", "TsutomuNihei", "Ciberpunk", "Cyborg001", "DocumentalIA"]
}

# Actualizar el proyecto 96
project = VideoProject.objects.get(id=96)
project.script_text = json.dumps(assemble_json, indent=4)
project.status = 'pending'
project.save()

print(f"✅ Proyecto 96 actualizado con rutas absolutas.")
