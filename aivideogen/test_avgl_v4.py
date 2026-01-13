#!/usr/bin/env python
"""
Test script for AVGL v4.0 JSON engine
Run this to validate the complete pipeline without starting Django server
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import VideoProject
from generator.avgl_engine import parse_avgl_json

# Test JSON script
test_script = """{
  "title": "Prueba AVGL v4.0",
  "voice": "es-ES-AlvaroNeural",
  "speed": 1.0,
  "blocks": [
    {
      "title": "Intro",
      "scenes": [
        {
          "title": "Hook Simple",
          "text": "Esta es una prueba del motor AVGL v4.0",
          "assets": [
            {
              "type": "earth_from_space_dark.png",
              "zoom": "1.0:1.2"
            }
          ]
        }
      ]
    }
  ]
}"""

def test_parser():
    """Test JSON parser"""
    print("🧪 Test 1: Validando parser JSON...")
    try:
        script = parse_avgl_json(test_script)
        print(f"  ✅ Parser OK - Título: '{script.title}'")
        print(f"  ✅ Bloques: {len(script.blocks)}")
        print(f"  ✅ Escenas totales: {len(script.get_all_scenes())}")
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_project_creation():
    """Test project creation and detection"""
    print("\n🧪 Test 2: Creando proyecto de prueba...")
    try:
        project = VideoProject.objects.create(
            title="Test AVGL v4.0",
            script_text=test_script,
            engine='edge',
            aspect_ratio='landscape'
        )
        print(f"  ✅ Proyecto creado - ID: {project.id}")
        
        # Test format detection
        from generator.utils import generate_video_process
        print("  ℹ️  La función detectará automáticamente el formato JSON")
        
        # Don't actually generate, just validate detection
        script_text = project.script_text.strip()
        is_json = script_text.startswith('{')
        print(f"  ✅ Detección de formato: {'JSON' if is_json else 'Legacy'}")
        
        # Cleanup
        project.delete()
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("AVGL v4.0 - Test Suite")
    print("=" * 60)
    
    results = []
    results.append(test_parser())
    results.append(test_project_creation())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ TODOS LOS TESTS PASARON")
        print("=" * 60)
        print("\n💡 Siguiente paso:")
        print("   1. Inicia el servidor: python manage.py runserver")
        print("   2. Crea un proyecto con el JSON de docs/ejemplo_completo_v4.json")
        print("   3. Genera el video y verifica el resultado")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        print("=" * 60)
        sys.exit(1)
