import os
import cv2
import subprocess
import sys
import site

# v22.1: Auto-discovery of user site-packages (Fix for --user installs not seen by some servers)
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.append(user_site)

try:
    import numpy as np
    from tqdm import tqdm
    import onnxruntime as ort
    import soundfile as sf
    from scipy import signal
    ONNX_AVAILABLE = True
except ImportError as e:
    ONNX_AVAILABLE = False
    print(f"⚠️ [LIP-SYNC] ERROR de Importación: {e}")
    print(f"DEBUG sys.path de este proceso: {sys.path}")
    print(f"DEBUG user_site buscado: {user_site}")

# Ruteo de FFmpeg detectado
FFMPEG_EXE = r"C:\Users\hp\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"

class LipSyncEngine:
    def __init__(self, model_path, detector_path, device="DmlExecutionProvider"):
        global ONNX_AVAILABLE
        if not ONNX_AVAILABLE:
            print("⚠️ [LIP-SYNC] Engine iniciado en modo DUMMY (Sin ONNX).")
            return
            
        self.providers = [device, 'CPUExecutionProvider'] if device == "DmlExecutionProvider" else [device]
        print(f"[*] Iniciando LipSyncEngine con providers: {self.providers}")
        
        try:
            self.session = ort.InferenceSession(model_path, providers=self.providers)
            self.detector = ort.InferenceSession(detector_path, providers=self.providers)
        except Exception as e:
            print(f"⚠️ [LIP-SYNC] Error al cargar modelos ONNX: {e}")
            ONNX_AVAILABLE = False
        
    def get_mel(self, audio_path):
        """
        Implementation of Mel Spectrogram without librosa (SciPy + NumPy)
        Optimized for Wav2Lip requirements (16kHz, 80 mels)
        """
        # 1. Load Audio
        wav, sr = sf.read(audio_path)
        if len(wav.shape) > 1: wav = np.mean(wav, axis=1) # Force Mono
        
        # 2. Resample to 16000 (Very basic linear resampling if needed)
        if sr != 16000:
            num_samples = int(len(wav) * 16000 / sr)
            wav = signal.resample(wav, num_samples)
            sr = 16000
            
        # 3. STFT (n_fft=800, hop=200, win=800)
        frequencies, times, stft_data = signal.stft(wav, fs=sr, nperseg=800, noverlap=600, nfft=800, boundary=None)
        magnitudes = np.abs(stft_data)
        
        # 4. Mel Filterbank (80 mels)
        # Simplified Mel filterbank creation
        def mel_filterbank(sr, n_fft, n_mels):
            f_min, f_max = 0, sr / 2
            mel_min = 2595 * np.log10(1 + f_min / 700)
            mel_max = 2595 * np.log10(1 + f_max / 700)
            mel_points = np.linspace(mel_min, mel_max, n_mels + 2)
            hz_points = 700 * (10**(mel_points / 2595) - 1)
            bin_points = np.floor((n_fft + 1) * hz_points / sr).astype(int)
            
            fb = np.zeros((n_mels, int(n_fft / 2 + 1)))
            for m in range(1, n_mels + 1):
                for k in range(bin_points[m-1], bin_points[m]):
                    fb[m-1, k] = (k - bin_points[m-1]) / (bin_points[m] - bin_points[m-1])
                for k in range(bin_points[m], bin_points[m+1]):
                    fb[m-1, k] = (bin_points[m+1] - k) / (bin_points[m+1] - bin_points[m])
            return fb

        fb = mel_filterbank(sr, 800, 80)
        mel = np.dot(fb, magnitudes)
        
        # 5. Log Dynamic Range Compression
        mel = np.log10(np.maximum(1e-5, mel))
        
        # 6. Normalization (ref=np.max like librosa.power_to_db)
        mel_max = np.max(mel)
        mel = 10 * (mel - mel_max) # Convert to dB relative to max
        
        # 7. Wav2Lip specific scaling
        mel = (mel + 40) / 40 
        return mel

    def detect_face(self, frame):
        # Ultraface ONNX (320x240)
        h, w = frame.shape[:2]
        img = cv2.resize(frame, (320, 240))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = (img - 127.0) / 128.0
        img = img.transpose(2, 0, 1).astype(np.float32)
        img = np.expand_dims(img, axis=0)
        
        confidences, boxes = self.detector.run(None, {self.detector.get_inputs()[0].name: img})
        
        # Tomar la mejor detección (simplificado)
        scores = confidences[0, :, 1]
        best_idx = np.argmax(scores)
        if scores[best_idx] < 0.5:
            return None # No face found
            
        box = boxes[0, best_idx]
        x1, y1, x2, y2 = int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)
        
        # Expandir un poco el área para incluir mentón y boca cómodamente
        padding = int((y2 - y1) * 0.2)
        return [max(0, x1-padding), max(0, y1-padding), min(w, x2+padding), min(h, y2+padding)]

    def get_mel(self, audio_path, duration=None):
        # 1. Load Audio
        wav, sr = sf.read(audio_path)
        if len(wav.shape) > 1: wav = np.mean(wav, axis=1) # Force Mono
        
        # v2.8: Clip audio to duration if specified
        if duration is not None:
            max_samples = int(duration * sr)
            if len(wav) > max_samples:
                wav = wav[:max_samples]
        
        # 2. Resample to 16000 (Very basic linear resampling if needed)
        # ... (Sigue igual)
        if sr != 16000:
            num_samples = int(len(wav) * 16000 / sr)
            wav = signal.resample(wav, num_samples)
            sr = 16000
            
        # 3. STFT
        frequencies, times, stft_data = signal.stft(wav, fs=sr, nperseg=800, noverlap=600, nfft=800, boundary=None)
        magnitudes = np.abs(stft_data)
        
        # ... (Lógica de Mel Filterbank sigue igual)
        fb = self.mel_filterbank(sr, 800, 80)
        mel = np.dot(fb, magnitudes)
        
        mel = np.log10(np.maximum(1e-5, mel))
        mel_max = np.max(mel)
        mel = 10 * (mel - mel_max)
        mel = (mel + 40) / 40 
        return mel

    def mel_filterbank(self, sr, n_fft, n_mels):
        f_min, f_max = 0, sr / 2
        mel_min = 2595 * np.log10(1 + f_min / 700)
        mel_max = 2595 * np.log10(1 + f_max / 700)
        mel_points = np.linspace(mel_min, mel_max, n_mels + 2)
        hz_points = 700 * (10**(mel_points / 2595) - 1)
        bin_points = np.floor((n_fft + 1) * hz_points / sr).astype(int)
        
        fb = np.zeros((n_mels, int(n_fft / 2 + 1)))
        for m in range(1, n_mels + 1):
            for k in range(bin_points[m-1], bin_points[m]):
                fb[m-1, k] = (k - bin_points[m-1]) / (bin_points[m] - bin_points[m-1])
            for k in range(bin_points[m], bin_points[m+1]):
                fb[m-1, k] = (bin_points[m+1] - k) / (bin_points[m+1] - bin_points[m])
        return fb

    def process_video(self, face_video_path, audio_path, output_path, start_time=0.0, end_time=None, duration=None):
        mel = self.get_mel(audio_path, duration=duration)
        
        # v2.8: Soporte para Modo Talking Head (Imágenes Estáticas)
        is_static_image = face_video_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
        
        start_frame = 0 
        if is_static_image:
            static_frame = cv2.imread(face_video_path)
            if static_frame is None: 
                raise ValueError(f"No se pudo cargar la imagen: {face_video_path}")
            fps = 25.0 
            height, width = static_frame.shape[:2]
            total_frames = int(mel.shape[1] / (16000 / fps / 200))
            print(f"[*] Modo Talking Head detectado: Generando {total_frames} frames.")
        else:
            video_cap = cv2.VideoCapture(face_video_path)
            if not video_cap.isOpened():
                raise ValueError(f"No se pudo abrir el video: {face_video_path}")
            fps = video_cap.get(cv2.CAP_PROP_FPS)
            width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            if start_time > 0:
                start_frame = int(start_time * fps)
                video_cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
                print(f"[*] Saltando a frame {start_frame} ({start_time}s)")

        # Inicializar frame_idx para logs
        frame_idx = start_frame

        temp_out = output_path.replace(".mp4", "_nosound.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_out, fourcc, fps, (width, height)) 

        print(f"[*] Sincronizando frames modo Ultra-HD Pro (v9.5) - Streaming Mode...")
        
        # Kernel de nitidez (Sharpening) para compensar el upscale
        sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])

        processed_count = 0
        pbar = tqdm(total=int(mel.shape[1] / (16000 / fps / 200))) # Estimar frames necesarios
        
        while True:
            if is_static_image:
                frame = static_frame.copy()
                ret = True
            else:
                ret, frame = video_cap.read()
            
            if not ret: 
                print("[*] Fin de video alcanzado.")
                break
            
            # Check for end_time (v21.0)
            # current_time = (start_frame + processed_count) / fps
            
            # Bypass logic if ONNX is missing
            if not ONNX_AVAILABLE:
                out.write(frame)
                processed_count += 1
                pbar.update(1)
                continue
                
            mel_idx = int(processed_count * (16000 / fps) / 200)
            if mel_idx + 16 > mel.shape[1]: 
                # v2.7: Break ALWAYS when audio finishes
                print(f"[*] Sincronización finalizada (Audio completo). Frames: {processed_count}")
                break
            
            mel_chunk = mel[:, mel_idx:mel_idx+16]
            mel_chunk = np.expand_dims(np.expand_dims(mel_chunk, 0), 0).astype(np.float32)

            orig_frame = frame.copy()
            
            # 1. Seguimiento de Rostro Dinámico (Frame-by-Frame)
            box = self.detect_face(orig_frame)
            if not box:
                out.write(orig_frame)
                processed_count += 1
                pbar.update(1)
                continue
            
            x1, y1, x2, y2 = box
            face_crop = orig_frame[y1:y2, x1:x2]
            if face_crop.size == 0: 
                out.write(orig_frame)
                frame_idx += 1
                pbar.update(1)
                continue
            
            fh, fw = face_crop.shape[:2]
            
            # 2. Wav2Lip
            face_96 = cv2.resize(face_crop, (96, 96))
            face_img = face_96.transpose(2, 0, 1).astype(np.float32) / 255.0
            face_img = np.expand_dims(face_img, 0)
            
            masked_face = face_img.copy()
            masked_face[:, :, 48:, :] = 0 
            vid_input = np.concatenate([masked_face, face_img], axis=1)

            inp = {
                self.session.get_inputs()[0].name: mel_chunk,
                self.session.get_inputs()[1].name: vid_input
            }
            res = self.session.run(None, inp)[0][0]
            
            # 3. Post-procesamiento Pro (Nitidez + Color)
            res_face = (res.transpose(1, 2, 0) * 255.0).astype(np.uint8)
            res_face = cv2.resize(res_face, (fw, fh))
            
            # Aplicar Nitidez (Sharpening) al parche para igualar HD
            res_face = cv2.filter2D(res_face, -1, sharpen_kernel)
            
            # Corrección de Color Dinámica
            for c in range(3):
                res_mean = np.mean(res_face[:,:,c])
                target_mean = np.mean(face_crop[:,:,c])
                res_face[:,:,c] = np.clip(res_face[:,:,c] * (target_mean / max(res_mean, 1)), 0, 255).astype(np.uint8)

            # 4. Mezclado Elíptico Pro + Protección de Oclusión (Luma Mask)
            mask = np.zeros((fh, fw), dtype=np.float32)
            center = (int(fw / 2), int(fh * 0.72)) 
            axes = (int(fw * 0.40), int(fh * 0.22))
            cv2.ellipse(mask, center, axes, 0, 0, 360, 1.0, -1)
            
            gray_orig = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
            _, occlusion_mask = cv2.threshold(gray_orig, 55, 255, cv2.THRESH_BINARY)
            occlusion_mask = occlusion_mask.astype(np.float32) / 255.0
            
            final_mask = mask * occlusion_mask
            final_mask = cv2.GaussianBlur(final_mask, (31, 31), 0)
            final_mask = np.expand_dims(final_mask, axis=-1)
            
            blended_face = (res_face * final_mask + face_crop * (1 - final_mask)).astype(np.uint8)
            
            # Pegar de nuevo en el frame original
            orig_frame[y1:y2, x1:x2] = blended_face
            out.write(orig_frame)
            
            # Marcador de éxito para el primer frame exitoso
            if frame_idx == 0 or frame_idx % 100 == 0:
                print(f"    [Lip-Sync] Frame {frame_idx} procesado con éxito (Face Found).")
            
            frame_idx += 1
            # v2.7: Actualizar contador de frames procesados
            processed_count += 1
            pbar.update(1)
        
        pbar.close()
        video_cap.release()
        
        out.release()
        
        # Merge final con FFmpeg
        cmd = [FFMPEG_EXE, "-y", "-i", temp_out, "-i", audio_path, "-c:v", "libx264", "-c:a", "aac", output_path]
        subprocess.run(cmd, check=True)
        os.remove(temp_out)
        print(f"[+] Video Pro (v9.4) generado en: {output_path}")

if __name__ == "__main__":
    WAV2LIP_MODEL = r"models\lipsync\wav2lip_gan.onnx"
    DETECTOR_MODEL = r"models\lipsync\face_detector.onnx"
    
    if os.path.exists(WAV2LIP_MODEL):
        engine = LipSyncEngine(WAV2LIP_MODEL, DETECTOR_MODEL)
        print("Módulo LipSyncEngine v0.1 (ONNX) listo para producción.")
    else:
        print("[-] Esperando descarga de modelos...")
