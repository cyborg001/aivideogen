import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import VideoProject

def inspect_latest_project():
    project = VideoProject.objects.order_by('-created_at').first()
    if not project:
        print("No projects found.")
        return

    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    print(f"--- Project ID: {project.id} ---")
    print(f"Title: {project.title}")
    print(f"Status: {project.status}")
    print(f"Hashtags Field: {project.script_hashtags}")
    print(f"Timestamps/Metadata Mapping Field: {project.timestamps}")
    print(f"YouTube ID: {project.youtube_video_id}")
    
    from generator.youtube_utils import generate_youtube_description
    description = generate_youtube_description(project)
    print("\n--- Generated YouTube Description ---")
    print(description)
    
    print("\n--- Final Tags Retrieval ---")
    # EXTRACT TAGS LOGIC (v4.2 - Smart Contextual Tags) from youtube_utils.py
    from generator.utils import extract_hashtags_from_script, generate_contextual_tags
    script_tags_str = project.script_hashtags or extract_hashtags_from_script(project.script_text)
    tags_list = [t.strip().replace('#', '') for t in script_tags_str.split() if t.strip()]
    contextual_tags = generate_contextual_tags(project)
    tags_list.extend(contextual_tags)
    
    final_tags = list(dict.fromkeys(tags_list))[:20]
    print(f"Final Tags: {final_tags}")

    print(f"\nLog Output (last 800 chars):\n{project.log_output[-800:]}")

if __name__ == "__main__":
    inspect_latest_project()
