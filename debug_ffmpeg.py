import os
import subprocess
import imageio_ffmpeg

def debug_ffmpeg():
    print("--- DIAGNOSTICO FFmpeg ---")
    try:
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        print(f"Path de imageio_ffmpeg: {ffmpeg_exe}")
        
        ffmpeg_dir = os.path.dirname(ffmpeg_exe)
        if ffmpeg_dir not in os.environ["PATH"]:
            os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]
            print(f"PATH actualizado con: {ffmpeg_dir}")
            
        print("Intentando ejecutar 'ffmpeg -version' via subprocess...")
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        print(f"Status: {result.returncode}")
        print(f"Output (1st line): {result.stdout.splitlines()[0] if result.stdout else 'VACIO'}")
        
        # Test whisper-like call (cmd only)
        print("Intentando llamar a 'ffmpeg' sin extensión (estilo Whisper)...")
        res2 = subprocess.run("ffmpeg -version", shell=True, capture_output=True, text=True)
        print(f"Status Shell: {res2.returncode}")
        
    except Exception as e:
        print(f"ERROR CRÍTICO: {str(e)}")

if __name__ == "__main__":
    debug_ffmpeg()
