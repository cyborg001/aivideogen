from moviepy import TextClip
import inspect

try:
    # Just a placeholder to see constructor and methods
    # We might need a dummy ImageMagick/Ghostscript if it's strictly required for init
    # but we can try dir() on the class itself
    print("Methods in TextClip class:")
    for method in sorted(dir(TextClip)):
        if not method.startswith("__"):
            print(f" - {method}")
except Exception as e:
    print(f"Error: {e}")
