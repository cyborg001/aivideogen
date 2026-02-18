
import time
from generator.models import VideoProject
from generator.utils import generate_video_process

def test_render():
    try:
        project_id = 63
        project = VideoProject.objects.get(id=project_id)
        print(f"Starting Render Test for Project: {project.title} (ID: {project.id})")
        print(f"scenes: {len(project.script_text)}") # Rough proxy, but we know it is 1 scene
        
        start_time = time.time()
        
        # Run the full process synchronously
        generate_video_process(project)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\nRender Context: {project.engine}")
        print(f"Total Duration: {duration:.2f} seconds")
        
    except Exception as e:
        print(f"Error testing render: {e}")
        import traceback
        traceback.print_exc()

test_render()
