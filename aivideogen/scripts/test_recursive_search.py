import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock settings and logger for the test
class MockSettings:
    MEDIA_ROOT = r'c:\Users\hp\aivideogen\aivideogen\media'
settings = MockSettings()

class ProjectLogger:
    def log(self, msg): 
        # Safely print messages avoiding Unicode issues in Windows console
        try:
            print(f"LOG: {msg}")
        except UnicodeEncodeError:
            print(f"LOG: {msg.encode('ascii', 'ignore').decode('ascii')}")

logger = ProjectLogger()

assets_dir = os.path.join(settings.MEDIA_ROOT, 'assets')
fname = "conquista_china_timelapse_v2.gif"

def test_recursive_search(fname):
    found_path = None
    logger.log(f"Searching for '{fname}' in subfolders...")
    for root, dirs, files in os.walk(assets_dir):
        if fname in files:
            found_path = os.path.join(root, fname)
            break
        # Case insensitive / extension check
        for f in files:
            name_no_ext, _ = os.path.splitext(f)
            if f.lower() == fname.lower() or name_no_ext.lower() == fname.lower():
                found_path = os.path.join(root, f)
                break
        if found_path: break
    return found_path

result = test_recursive_search(fname)
if result:
    print(f"SUCCESS: Found at {result}")
else:
    print("FAILURE: Not found.")

# Test case insensitive
result_ci = test_recursive_search("CONQUISTA_CHINA_TIMELAPSE_V2.GIF")
if result_ci:
    print(f"SUCCESS (CI): Found at {result_ci}")

# Test no extension
result_ne = test_recursive_search("conquista_china_timelapse_v2")
if result_ne:
    print(f"SUCCESS (NE): Found at {result_ne}")
