
import os
import sys
import django
import json

# Setup Django
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import VideoProject

def check_latest_project():
    try:
        # Check Project ID 274
        try:
            project = VideoProject.objects.get(id=274)
        except:
            print("Project 274 not found.")
            return

        print(f"--------------------------------------------------")
        print(f"Checking Project: {project.title} (ID: {project.id})")
        
        raw_text = project.script_text
        print(f"Script Length: {len(raw_text)} chars")
        
        target_pos = 8913
        start = max(0, target_pos - 100)
        end = min(len(raw_text), target_pos + 100)
        snippet = raw_text[start:end]
        print(f"Context around {target_pos}:")
        print(f"...{snippet}...")
        
        try:
            parsed = json.loads(raw_text)
            print("✅ JSON is VALID.")
        except json.JSONDecodeError as e:
            print(f"❌ JSON ERROR: {e}")
            print(f"Error at char: {e.pos}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_latest_project()
