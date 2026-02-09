import tkinter as tk
from tkinter import filedialog
import sys
import json

def main():
    try:
        filter_type = sys.argv[1] if len(sys.argv) > 1 else 'visual'
        
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
            print(json.dumps({'status': 'cancelled'}))
        else:
            import os
            print(json.dumps({
                'status': 'success',
                'path': file_path,
                'filename': os.path.basename(file_path)
            }))
            
    except Exception as e:
        print(json.dumps({'status': 'error', 'error': str(e)}))

if __name__ == "__main__":
    main()
