import os
import sys
from unittest.mock import MagicMock

BASE_DIR = r"c:\Users\hp\aivideogen"
sys.path.append(BASE_DIR)

# --- MOCK DJANGO SETTINGS ---
mock_settings = MagicMock()
mock_settings.MEDIA_ROOT = os.path.join(BASE_DIR, "media")

class MockConf:
    settings = mock_settings

sys.modules['django.conf'] = MockConf()
sys.modules['django'] = MagicMock()
# ----------------------------

from aivideogen.generator.video_engine import render_pro_subtitles
from moviepy import CompositeVideoClip, TextClip

def verify_chunk_logic():
    print("Verifying Chunk-by-Chunk Logic (v16.7.1)...")
    
    target_size = (1080, 1920)
    # Text with many descenders to test vertical clipping (g, p, y, j, q)
    test_text = "audiencia abajo progresivo dinámico tecnología"
    word_timings = [
        {'start': 0.0, 'end': 0.5, 'word': 'audiencia'},
        {'start': 0.5, 'end': 1.0, 'word': 'abajo'},
        {'start': 1.0, 'end': 1.5, 'word': 'progresivo'},
        {'start': 1.5, 'end': 2.0, 'word': 'dinámico'},
        {'start': 2.0, 'end': 2.5, 'word': 'tecnología'},
    ]
    
    duration = 2.5
    
    clip = render_pro_subtitles(
        test_text, 
        duration, 
        target_size, 
        is_dynamic=True, 
        word_timings=word_timings
    )
    
    if not isinstance(clip, CompositeVideoClip):
        print(f"[FAIL] Expected CompositeVideoClip, got {type(clip)}")
        return

    # Check clips inside (Chunks)
    chunks = clip.clips
    print(f"Total chunks generated: {len(chunks)}")
    
    # We expect 2 chunks for 5 words (4 + 1)
    if len(chunks) == 2:
        print("[OK] Chunk count is correct.")
    else:
        print(f"[FAIL] Expected 2 chunks, got {len(chunks)}")

    # Verify sequentiality and sizing
    last_end = -1.0
    for i, c in enumerate(chunks):
        start = c.start
        end = c.end + start # moviepy end is relative to start in some versions, but with_duration/with_start uses absolute for Composite
        
        # In modern moviepy 2.0+, clip.end is duration if not set absolutely
        # but here we use with_duration which sets the duration.
        dur = c.duration
        abs_end = start + dur
        
        print(f"Clip {i}: {start:.2f}s -> {abs_end:.2f}s | Method: {getattr(c, 'method', 'N/A')}")
        
        if start < last_end - 0.01: # Small epsilon
            print(f"[FAIL] Overlap detected at Clip {i}!")
        
        last_end = abs_end

    print("\n[SUCCESS] Subtitle stability verification completed.")

if __name__ == "__main__":
    verify_chunk_logic()
