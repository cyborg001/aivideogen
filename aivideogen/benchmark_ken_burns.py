
import time
import os
import sys
import numpy as np
from PIL import Image

# Add project root to path
PROJECT_ROOT = r"c:\Users\hp\aivideogen\aivideogen"
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

import django
from django.conf import settings

if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from generator.video_engine import apply_ken_burns

def log(msg):
    sys.stderr.write(f"{msg}\n")
    sys.stderr.flush()

def create_dummy_image(path, size=(1920, 1080)):
    if os.path.exists(path): return path
    img = Image.new('RGB', size, color=(100, 150, 200))
    img_np = np.array(img)
    img_np[::50, ::50] = [255, 255, 255]
    Image.fromarray(img_np).save(path)
    return path

def benchmark():
    asset_path = "temp_benchmark_asset.png"
    output_path = "temp_benchmark_out.mp4"
    
    try:
        create_dummy_image(asset_path)
        
        duration = 5.0
        target_size = (1080, 1920) # Vertical generic
        
        log(f"--- Benchmarking apply_ken_burns ({duration}s, {target_size}) ---")
        
        start_time = time.time()
        
        # Call the function under test
        clip = apply_ken_burns(
            image_path=asset_path,
            duration=duration,
            target_size=target_size,
            zoom="1.0:1.5",
            move="VER"
        )
        
        setup_time = time.time() - start_time
        log(f"Setup time: {setup_time:.4f}s")
        
        render_start = time.time()
        # Render to os.devnull or file
        # Using ultrafast to isolate generation speed
        clip.write_videofile(
            output_path, 
            fps=30, 
            codec="libx264", 
            preset="ultrafast", 
            threads=4,
            logger=None 
        )
        
        render_time = time.time() - render_start
        log(f"Render time: {render_time:.4f}s")
        fps = 30 * duration / render_time
        log(f"FPS: {fps:.2f}")
        
    except Exception as e:
        log(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if os.path.exists(asset_path):
            os.remove(asset_path)
        if os.path.exists(output_path):
            os.remove(output_path)

if __name__ == "__main__":
    benchmark()
