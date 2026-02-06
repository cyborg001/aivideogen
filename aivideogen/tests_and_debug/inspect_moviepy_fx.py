try:
    from moviepy.video import vfx
    print("Methods in moviepy.video.vfx:")
    for method in sorted(dir(vfx)):
        if not method.startswith("__"):
            print(f" - {method}")
except Exception as e:
    print(f"Error checking vfx: {e}")

try:
    from moviepy.video.Clip import Clip
    print("\nMethods in Clip base class:")
    for method in sorted(dir(Clip)):
        if not method.startswith("__"):
            print(f" - {method}")
except Exception as e:
    print(f"Error checking Clip: {e}")
