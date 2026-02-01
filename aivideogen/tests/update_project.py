import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aivideogen.settings')
django.setup()

from generator.models import VideoProject

def update_project():
    try:
        project_id = 206  # Target Project
        json_path = r"c:\Users\Usuario\Documents\curso creacion contenido con ia\guiones\capitulo_1_ethan_vertical.json"
        
        with open(json_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
            
        project = VideoProject.objects.get(id=project_id)
        project.script_text = script_content
        project.status = 'pending' # Reset status
        project.save()
        
        print(f"✅ Project {project_id} updated successfully with local JSON.")
        print(f"   Voice check: {'Jorge' in script_content}")
        
    except VideoProject.DoesNotExist:
        print(f"❌ Project {project_id} not found. Trying 205...")
        # Fallback to 205 just in case
        try:
             project = VideoProject.objects.get(id=205)
             project.script_text = script_content
             project.save()
             print(f"✅ Project 205 updated instead.")
        except:
            print("❌ No project found.")
            
if __name__ == "__main__":
    update_project()
