import os
import shutil
import re

ASSETS_DIR = r"c:\Users\Usuario\Documents\curso creacion contenido con ia\aivideogen3\aivideogen\media\assets"

def normalize_assets():
    print(f"Scanning {ASSETS_DIR}...")
    files = os.listdir(ASSETS_DIR)
    
    # Regex to find timestamp suffixes (e.g., _1768467192367)
    # Assumes timestamp is at the end of filename before extension
    # Looking for _\d{10,}
    pattern = re.compile(r'(.+)_(\d{10,})\.(png|jpg|jpeg|mp4)$')
    
    count = 0
    for f in files:
        match = pattern.match(f)
        if match:
            base_name = match.group(1)
            ext = match.group(3)
            clean_name = f"{base_name}.{ext}"
            
            src = os.path.join(ASSETS_DIR, f)
            dst = os.path.join(ASSETS_DIR, clean_name)
            
            if not os.path.exists(dst):
                print(f"Normalizing: {f} -> {clean_name}")
                shutil.copy2(src, dst)
                count += 1
            else:
                print(f"Skipping {f}, {clean_name} already exists.")
                
    print(f"Done. Generalized {count} assets.")

if __name__ == "__main__":
    normalize_assets()
