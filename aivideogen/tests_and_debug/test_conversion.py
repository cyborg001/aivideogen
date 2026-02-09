
import sys
import os
import json
import django

# Setup Django environment
# Add the inner folder to path so we can import 'config' and 'generator'
sys.path.append(os.path.join(os.getcwd(), 'aivideogen')) 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
try:
    django.setup()
except Exception as e:
    print(f"Django setup failed: {e}")
    # Fallback/Debug
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    django.setup()

from generator.avgl_engine import convert_avgl_json_to_text

def test_conversion():
    file_path = 'aivideogen/guiones/tesla_model_pi.json'
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Testing conversion for {file_path}...")
        text_output = convert_avgl_json_to_text(data)
        print("Conversion SUCCESS!")
        print("--- START OUTPUT ---")
        print(text_output[:500] + "...") 
        print("--- END OUTPUT ---")
        
    except Exception as e:
        print(f"Conversion FAILED: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_conversion()
