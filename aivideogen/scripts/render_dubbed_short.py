import os
import sys
import json
import asyncio
import subprocess

# Configurar Django para usar generator.utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aivideogen.settings')
try:
    import django
    django.setup()
except Exception as e:
    print(f"[*] Advertencia Django: {e} (Continuando si es posible)")

from moviepy import VideoFileClip, concatenate_videoclips, AudioFileClip
from scripts.local_lipsync import LipSyncEngine, FFMPEG_EXE
from generator.utils import generate_audio_edge

class DubbingOrchestrator:
    def __init__(self, output_dir="media/dubbed_shorts"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Rutas de modelos
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        model_path = os.path.join(root, "models", "lipsync", "wav2lip_gan.onnx")
        detector_path = os.path.join(root, "models", "lipsync", "face_detector.onnx")
        
        self.lipsync_engine = LipSyncEngine(model_path=model_path, detector_path=detector_path)

    async def render_segment(self, video_path, segment, idx, lipsync=True):
        start = segment["start_time"]
        end = segment["end_time"]
        text = segment["text"]
        
        print(f"[*] Procesando segmento {idx} ({'CON' if lipsync else 'SIN'} LipSync): {start}s -> {end}s")
        
        # 1. Cortar clip original
        full_clip = VideoFileClip(video_path)
        sub_clip = full_clip.subclipped(start, end)
        
        # 2. Generar audio en español
        temp_audio = os.path.join(self.output_dir, f"temp_audio_{idx}.mp3")
        await generate_audio_edge(text, temp_audio, voice="es-US-AlonsoNeural", rate="+5%")
        
        output_final = os.path.join(self.output_dir, f"final_hq_{idx}.mp4")
        
        if os.path.exists(output_final) and os.path.getsize(output_final) > 1024:
            print(f"[*] Saltando segmento {idx} (Ya existe: {output_final})")
            return output_final
        
        # 1. Generar Audio (TTS)
        if lipsync:
            # 3. Aplicar Lip-Sync (IA)
            temp_video = os.path.join(self.output_dir, f"temp_clip_{idx}.mp4")
            sub_clip.write_videofile(temp_video, audio=False, codec="libx264", preset="ultrafast")
            self.lipsync_engine.process_video(temp_video, temp_audio, output_final)
            if os.path.exists(temp_video): os.remove(temp_video)
        else:
            # 3. Mezclar audio directamente (Rápido - Estilo Documental con Ducking)
            original_audio = sub_clip.audio.with_volume_scaled(0.15) # Atenuar original al 15%
            translated_audio = AudioFileClip(temp_audio)
            
            from moviepy import CompositeAudioClip
            composite_audio = CompositeAudioClip([original_audio, translated_audio])
            
            final_sub = sub_clip.with_audio(composite_audio)
            final_sub.write_videofile(output_final, codec="libx264", audio_codec="aac", 
                                     temp_audiofile=os.path.join(self.output_dir, f"temp_aud_{idx}.mp4"),
                                     remove_temp=True, fps=sub_clip.fps, preset="slow", bitrate="5000k")
            translated_audio.close()

        # Limpiar temporales
        full_clip.close()
        sub_clip.close()
        if os.path.exists(temp_audio): os.remove(temp_audio)
        
        return output_final

    async def process_avgl(self, video_path, avgl_path):
        with open(avgl_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        final_clips_paths = []
        global_lipsync = data.get("config", {}).get("lipsync", True)
        
        for i, segment in enumerate(data["script"]):
            try:
                # El clip individual puede sobreescribir el global si se desea
                segment_lipsync = segment.get("lipsync", global_lipsync)
                clip_path = await self.render_segment(video_path, segment, i, lipsync=segment_lipsync)
                final_clips_paths.append(clip_path)
            except Exception as e:
                print(f"[-] Error en segmento {i}: {e}")
        
        # 4. Concatenar clips finales con FFmpeg (más robusto)
        print("[*] Concatenando clips finales con FFmpeg...")
        list_file = os.path.join(self.output_dir, "concat_list.txt")
        with open(list_file, "w") as f:
            for p in final_clips_paths:
                # FFmpeg necesita rutas con barras normales o escapadas
                clean_p = os.path.abspath(p).replace("\\", "/")
                f.write(f"file '{clean_p}'\n")
        
        out_name = os.path.basename(video_path).rsplit(".", 1)[0] + "_DUBBED.mp4"
        out_path = os.path.join(self.output_dir, out_name)

        # v9.6.2: Re-encode en la unión final para asegurar compatibilidad total y evitar truncado
        cmd = [FFMPEG_EXE, "-y", "-f", "concat", "-safe", "0", "-i", list_file, 
               "-c:v", "libx264", "-preset", "fast", "-b:v", "5000k", "-c:a", "aac", out_path]
        subprocess.run(cmd, check=True)
        
        if os.path.exists(list_file): os.remove(list_file)
        print(f"[+] ¡Doblaje completado! Archivo final: {out_path}")
        return out_path

async def main():
    import sys
    if len(sys.argv) < 3:
        print("Uso: python scripts/render_dubbed_short.py <video_original> <avgl_json>")
        return

    orch = DubbingOrchestrator()
    await orch.process_avgl(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    asyncio.run(main())
