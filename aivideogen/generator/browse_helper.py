import tkinter as tk
from tkinter import filedialog
import sys
import json

def run_file_dialog(filter_type='visual', multiple=False):
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        if filter_type == 'audio':
            dialog_title = "Seleccionar Audio (SFX/Música)"
            file_types = [
                ("Archivos de Audio (*.mp3, *.wav, *.aac)", "*.mp3 *.wav *.aac *.ogg *.m4a *.flac *.webm"),
                ("Todo", "*.*")
            ]
        else:
            dialog_title = "Seleccionar Imágenes o Videos"
            file_types = [
                ("Imágenes y Videos (*.png, *.jpg, *.mp4)", "*.png *.jpg *.jpeg *.mp4 *.mov *.avi *.webm *.gif"),
                ("Imágenes (*.png, *.jpg)", "*.png *.jpg *.jpeg *.gif"),
                ("Videos (*.mp4, *.avi)", "*.mp4 *.mov *.avi *.webm"),
                ("Todo", "*.*")
            ]
            
        if multiple:
            file_paths = filedialog.askopenfilenames(
                title=dialog_title,
                filetypes=file_types
            )
            
            root.destroy()
            if not file_paths:
                return {'status': 'cancelled'}
            
            return {
                'status': 'success',
                'paths': list(file_paths),
                'count': len(file_paths)
            }
        else:
            file_path = filedialog.askopenfilename(
                title=dialog_title,
                filetypes=file_types
            )
            
            root.destroy()
            if not file_path:
                return {'status': 'cancelled'}
            
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
    # v13.6: Multi-select support via second or third argument
    filter_type = 'visual'
    multiple = False
    
    if "--browse" in sys.argv:
        idx = sys.argv.index("--browse")
        if len(sys.argv) > idx + 1: filter_type = sys.argv[idx + 1]
    elif len(sys.argv) > 1:
        filter_type = sys.argv[1]

    if "multiple" in sys.argv or "--multiple" in sys.argv:
        multiple = True
    
    result = run_file_dialog(filter_type, multiple=multiple)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
