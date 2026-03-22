import os
import whisper
import json
import subprocess
import sys
from datetime import timedelta

# Asegurar que ffmpeg esté en el PATH para Whisper
FFMPEG_DIR = r"C:\Users\hp\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries"
if FFMPEG_DIR not in os.environ["PATH"]:
    os.environ["PATH"] += os.pathsep + FFMPEG_DIR

class Transcriber:
    def __init__(self, model_size="base"):
        print(f"[*] Cargando modelo Whisper ({model_size})...")
        self.model = whisper.load_model(model_size)

    def extract_audio(self, video_path):
        audio_path = video_path.rsplit(".", 1)[0] + ".wav"
        print(f"[*] Extrayendo audio a: {audio_path}")
        ffmpeg_exe = r"C:\Users\hp\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
        cmd = [
            ffmpeg_exe, "-y", "-i", video_path,
            "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
            audio_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return audio_path

    def transcribe(self, video_path):
        audio_path = self.extract_audio(video_path)
        print(f"[*] Transcribiendo discurso...")
        result = self.model.transcribe(audio_path, verbose=False)
        
        # Limpiar audio temporal
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
        return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python transcribe_video.py <video_path>")
        sys.exit(1)
        
    video_file = sys.argv[1]
    if not os.path.exists(video_file):
        print(f"[-] El archivo no existe: {video_file}")
        sys.exit(1)
        
    transcriber = Transcriber()
    res = transcriber.transcribe(video_file)
    
    # Guardar resultado en JSON
    out_json = video_file.rsplit(".", 1)[0] + "_transcript.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=4, ensure_ascii=False)
        
    print(f"[+] Transcripción completada: {out_json}")
    print(f" Texto detectado: {res['text'][:100]}...")
