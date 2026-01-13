import os
import sys
import django
import numpy as np
from PIL import Image

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.video_engine import apply_ken_burns

def test_motion():
    print("Testing v4.1 Zoom and Move...")
    target_size = (1920, 1080)
    duration = 2.0
    
    # Use a real image from assets
    assets_dir = os.path.join("media", "assets")
    real_images = [f for f in os.listdir(assets_dir) if f.lower().endswith(('.png', '.jpg'))]
    
    if not real_images:
        print("No images found in media/assets")
        return
        
    image_path = os.path.join(assets_dir, real_images[0])
    
    # Test Zoom + Move
    print(f"Applying Zoom 1.0:1.5 and Move HOR:0:100 to {image_path}")
    clip = apply_ken_burns(image_path, duration, target_size, zoom="1.0:1.5", move="HOR:0:100")
    
    # Verify frame 0 and frame end
    f0 = clip.get_frame(0)
    fn = clip.get_frame(duration - 0.1)
    
    # If they are different, motion is happening
    diff = np.sum(np.abs(f0.astype(float) - fn.astype(float)))
    print(f"Pixel difference between start and end: {diff}")
    
    if diff > 1000:
        print("✅ MOTION DETECTED!")
    else:
        print("❌ NO MOTION DETECTED. The frames are identical.")

if __name__ == "__main__":
    test_motion()
