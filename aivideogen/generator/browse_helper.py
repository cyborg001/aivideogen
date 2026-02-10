import tkinter as tk
from tkinter import filedialog
import sys
import json

def run_file_dialog(filter_type='visual'):
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        if filter_type == 'audio':
            dialog_title = "Seleccionar Archivo de Audio (SFX/Música)"
            file_types = [
                ("Audio Files", "*.mp3 *.wav *.aac *.ogg *.m4a *.flac *.webm"),
                ("MP3", "*.mp3"),
                ("WAV", "*.wav"),
                ("WebM Audio", "*.webm"),
                ("All files", "*.*")
            ]
        else:
            dialog_title = "Seleccionar Asset (Imagen o Video)"
            file_types = [
                ("Media Files", "*.png *.jpg *.jpeg *.mp4 *.mov *.avi *.webm *.gif"),
                ("Images", "*.png *.jpg *.jpeg *.gif"),
                ("Videos", "*.mp4 *.mov *.avi *.webm"),
                ("All files", "*.*")
            ]
            
        file_path = filedialog.askopenfilename(
            title=dialog_title,
            filetypes=file_types
        )
        
        root.destroy()
        
        if not file_path:
            return {'status': 'cancelled'}
        else:
            import os
            return {
                'status': 'success',
                'path': file_path,
                'filename': os.path.basename(file_path)
            }
            
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def main():
    import json
    # v13.5/6: Smart arg parsing for routed calls
    filter_type = 'visual'
    if "--browse" in sys.argv:
        idx = sys.argv.index("--browse")
        if len(sys.argv) > idx + 1:
            filter_type = sys.argv[idx + 1]
    elif len(sys.argv) > 1:
        filter_type = sys.argv[1]
    
    result = run_file_dialog(filter_type)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
