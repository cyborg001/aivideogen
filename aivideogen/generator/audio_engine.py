import numpy as np
import os
import wave
import re
from moviepy import CompositeAudioClip
from datetime import datetime

class PCMRadar:
    """
    Radar de alta sensibilidad para detección de actividad vocal en archivos de audio.
    Soporta análisis directo PCM para WAV y fallback mediante MoviePy para otros formatos.
    """
    @staticmethod
    def analyze_ia_voice(audio_clip, logger=None, threshold=0.02, sample_rate=20):
        """
        [IA-RADAR v1.0] Optimizado para voces digitales limpias (Edge-TTS, ElevenLabs).
        Detecta pausas quirúrgicas para permitir que la música suba en silencios cortos.
        """
        try:
            # IA usa 20fps para mayor precisión en pausas rápidas
            fps = sample_rate
            s_array = audio_clip.to_soundarray(fps=fps)
            
            if len(s_array.shape) > 1:
                volumes = np.abs(s_array).max(axis=1)
            else:
                volumes = np.abs(s_array)
            
            # Normalización interna para IA (asegura que el umbral sea relativo)
            max_vol = np.max(volumes) if len(volumes) > 0 else 0
            if logger: logger.log(f"      🤖 [IA-Radar] Energía Máxima: {max_vol:.4f} (Umbral Relativo: {threshold})")
            if max_vol > 0: volumes = volumes / max_vol
            
            # Umbral agresivo para IA limpia
            is_voice = volumes > threshold
            
            intervals = []
            start = None
            for i, val in enumerate(is_voice):
                if val and start is None:
                    start = i / fps
                elif not val and start is not None:
                    intervals.append((start, i / fps))
                    start = None
            if start is not None:
                intervals.append((start, len(is_voice) / fps))
            
            if logger: logger.log(f"      🤖 [IA-Radar] {len(intervals)} ráfagas de voz detectadas.")
            return intervals
        except Exception as e:
            if logger: logger.log(f"      ⚠️ [IA-Radar] Error: {e}")
            return [(0, audio_clip.duration)]

    @staticmethod
    def analyze(audio_clip, logger=None, threshold=0.05, sample_rate=10):
        """
        Analiza la energía del audio para detección de voz.
        ⚠️ [ARQUITECTO]: NO usar para voces de IA si se requiere bloque sólido.
        Esta función es para detección granular de pausas.
        """
        try:
            fps = sample_rate
            # v5.9.4: Use soundarray to respect subclips/offsets (Fixes the 11k second jump)
            s_array = audio_clip.to_soundarray(fps=fps)
                
            if len(s_array.shape) > 1:
                volumes = np.abs(s_array).max(axis=1)
            else:
                volumes = np.abs(s_array)
                
            peak = np.max(volumes) if len(volumes) > 0 else 0
            if logger: 
                avg_vol = np.mean(volumes) if len(volumes) > 0 else 0
                logger.log(f"    📊 [Radar] Volumen Medio: {avg_vol:.4f} | Pico: {peak:.4f} (Umbral: {threshold})")
            
            intervals = []
            is_talking = False
            start_t = 0
            
            for i, vol in enumerate(volumes):
                t = i / fps
                if vol > threshold:
                    if not is_talking:
                        is_talking = True
                        voice_start = t
                else:
                    if is_talking:
                        is_talking = False
                        # v40.8: Duration Filter (Ignore bursts shorter than 100ms)
                        # Prevents "0.00s" intervals that break ducking logic
                        if (t - voice_start) >= 0.1:
                            intervals.append((voice_start, t))
                            if logger: logger.log(f"      📍 [Radar] Voz detectada: {voice_start:.2f}s - {t:.2f}s (Dur: {t-voice_start:.2f}s)")
                        else:
                            if logger: logger.log(f"      🧹 [Radar] Ignorando ráfaga corta ({t-voice_start:.2f}s)")
            
            if is_talking:
                intervals.append((voice_start, len(volumes)/fps))
                
            return intervals
        except Exception as e:
            if logger: logger.log(f"    🚨 [Radar] Error crítico de análisis: {e}")
            return []

    @staticmethod
    def analyze_custom_audio(audio_clip, logger=None, threshold=0.05, sample_rate=20):
        """
        v40.21: PURE BINARY SCAN (Wave Module).
        Inmunidad Absoluta: Salta MoviePy para leer audio directamente del disco.
        """
        import numpy as np
        import os
        import uuid
        import wave

        if not audio_clip: return []

        # 1. Export strictly to PCM WAV (16-bit)
        temp_wav = f"temp_radar_{uuid.uuid4().hex[:8]}.wav"
        if logger: logger.log(f"    [Radar-Manual] Exportando WAV para escaneo binario...")
        
        try:
            audio_clip.write_audiofile(temp_wav, codec='pcm_s16le', fps=22050, logger=None)
        except Exception as e:
            if logger: logger.log(f"    [Radar-Manual] Error al exportar: {e}")
            return []

        if not os.path.exists(temp_wav):
            return []

        try:
            # 2. Open via 'wave' module
            with wave.open(temp_wav, 'rb') as wf:
                n_frames = wf.getnframes()
                raw_data = wf.readframes(n_frames)
                data = np.frombuffer(raw_data, dtype=np.int16)
                
                n_channels = wf.getnchannels()
                if n_channels > 1:
                    data = data.reshape(-1, n_channels)
                    data = data.mean(axis=1)
                
                orig_fps = wf.getframerate()
                step = max(1, orig_fps // sample_rate)
                n_chunks = len(data) // step
                if n_chunks > 0:
                    chunks = data[:n_chunks * step].reshape(n_chunks, step)
                    energy = np.max(np.abs(chunks), axis=1) / 32767.0
                else:
                    energy = np.abs(data) / 32767.0
        except Exception as e:
            if logger: logger.log(f"    [Radar-Manual] Error en lectura binaria: {e}")
            energy = np.array([])
        finally:
            try: os.remove(temp_wav)
            except: pass

        if energy.size == 0:
            return []

        max_e = np.max(energy)
        eff_threshold = threshold if threshold is not None else 0.05
        if max_e > 0.001 and eff_threshold > (max_e * 0.5):
            eff_threshold = max_e * 0.4
        if eff_threshold < 0.008: eff_threshold = 0.008

        if logger: logger.log(f"    [Radar-Manual] Escaneo Binario OK: Umbral {eff_threshold:.4f} | Pico: {max_e:.4f}")

        intervals = []
        is_talking = False
        start_t = 0
        fps_float = float(sample_rate)

        for i, e in enumerate(energy):
            t = i / fps_float
            if e >= eff_threshold:
                if not is_talking:
                    start_t = t
                    is_talking = True
            else:
                if is_talking:
                    if (t - start_t) > 0.05:
                        intervals.append((start_t, t))
                    is_talking = False

        if is_talking:
            intervals.append((start_t, len(energy) / fps_float))

        return intervals


class IntervalManager:
    """
    Gestor de intervalos de tiempo para optimizar la 'respiración' musical.
    """
    @staticmethod
    def merge(intervals, threshold=0.3):
        """
        Fusiona intervalos de voz cercanos para evitar que la música suba y baje muy rápido.
        """
        if not intervals: return []
        
        sorted_intervals = sorted(intervals, key=lambda x: x[0])
        merged = []
        if not sorted_intervals: return []
        
        curr_start, curr_end = sorted_intervals[0]
        
        for next_start, next_end in sorted_intervals[1:]:
            if next_start - curr_end <= threshold:
                curr_end = max(curr_end, next_end)
            else:
                merged.append((curr_start, curr_end))
                curr_start, curr_end = next_start, next_end
        
        merged.append((curr_start, curr_end))
        return merged

class DuckingMaster:
    """
    Motor Maestro de Mezcla. Implementa las rampas matemáticas robustas (v28 Heritage).
    """
    @staticmethod
    def create_ducking_transform(intervals, vol, dr, att, rel, block_dur, fade_in=0, early_finish=0):
        """
        Crea una función de transformación (MoviePy) con rampas de ataque/relajación protegidas.
        """
        def apply_ducking(get_frame, t):
            audio = get_frame(t)
            if isinstance(t, np.ndarray):
                factors = np.full(t.shape, float(vol))
                for vs, ve in intervals:
                    # 1. Ataque (Música baja)
                    m_attack = (t >= (vs - att)) & (t < vs)
                    if np.any(m_attack):
                        p = (t[m_attack] - (vs - att)) / att
                        factors[m_attack] = np.minimum(factors[m_attack], vol * (1.0 - p * (1.0 - dr)))
                    
                    # 2. Ducked (Voz activa) - PRIORIDAD DE SILENCIO ABSOLUTO
                    factors[(t >= vs) & (t <= ve)] = vol * dr
                    
                    # 3. Relajación (Música sube)
                    m_release = (t > ve) & (t <= (ve + rel))
                    if np.any(m_release):
                        p = (t[m_release] - ve) / rel
                        factors[m_release] = np.minimum(factors[m_release], vol * (dr + p * (1.0 - dr)))
                
                # Capas de seguridad de Bloque (Fade In / Early Finish)
                if fade_in > 0:
                    factors[t < fade_in] *= (t[t < fade_in] / fade_in)
                
                if early_finish > 0:
                    m_silent = t > (block_dur - early_finish)
                    factors[m_silent] = 0.0
                    m_pre_fade = (t >= (block_dur - early_finish - fade_in)) & (t <= (block_dur - early_finish))
                    if np.any(m_pre_fade):
                        p_out = (block_dur - early_finish - t[m_pre_fade]) / fade_in
                        factors[m_pre_fade] *= np.maximum(0, np.minimum(1, p_out))
                
                return audio * factors[:, None]
            else:
                # Lógica escalar
                factor = float(vol)
                for vs, ve in intervals:
                    if vs <= t <= ve: factor = vol * dr; break
                    elif (vs - att) <= t < vs:
                        p = (t - (vs - att)) / att
                        factor = min(factor, vol * (1.0 - p * (1.0 - dr)))
                    elif ve < t <= (ve + rel):
                        p = (t - ve) / rel
                        factor = min(factor, vol * (dr + p * (1.0 - dr)))
                
                if fade_in > 0 and t < fade_in: factor *= (t / fade_in)
                if early_finish > 0:
                    if t > (block_dur - early_finish): factor = 0.0
                    elif (block_dur - early_finish - fade_in) <= t <= (block_dur - early_finish):
                        p_out = (block_dur - early_finish - t) / fade_in
                        factor *= max(0, min(1, p_out))
                
                return audio * factor
                
        return apply_ducking

    @staticmethod
    def create_global_transform(merged_intervals, block_time_ranges, mute_intervals, duck_ratio, att, rel, default_vol):
        """
        Crea una función de transformación global compleja para la música de fondo continua.
        Soporta volúmenes dinámicos por bloque e intervalos de silencio forzado.
        """
        def apply_global_ducking(get_frame, t):
            audio = get_frame(t)
            if isinstance(t, np.ndarray):
                # 1. Base Volume por Bloque
                base_vols = np.full(t.shape, float(default_vol))
                for b_start, b_end, b_vol in block_time_ranges:
                    mask = (t >= b_start) & (t <= b_end)
                    base_vols[mask] = b_vol
                
                # 2. Ducking Factors (Rampas de voz)
                factors = np.ones_like(t, dtype=float)
                for v_start, v_end in merged_intervals:
                    # Attack
                    m_attack = (t >= (v_start - att)) & (t < v_start)
                    if np.any(m_attack):
                        p = (t[m_attack] - (v_start - att)) / att
                        factors[m_attack] = np.minimum(factors[m_attack], 1.0 - (p * (1.0 - duck_ratio)))
                    
                    # Ducked
                    factors[(t >= v_start) & (t <= v_end)] = duck_ratio
                    
                    # Release
                    m_release = (t > v_end) & (t <= (v_end + rel))
                    if np.any(m_release):
                        p = (t[m_release] - v_end) / rel
                        factors[m_release] = np.minimum(factors[m_release], duck_ratio + (p * (1.0 - duck_ratio)))
                
                # 3. Mute Intervals (Donde hay música local)
                for ms, me in mute_intervals:
                    factors[(t >= ms) & (t <= me)] = 0.0
                
                return audio * (base_vols[:, None] * factors[:, None])
            else:
                # Lógica Escalar
                cur_peak = default_vol
                for b_start, b_end, b_vol in block_time_ranges:
                    if b_start <= t <= b_end: cur_peak = b_vol; break
                
                # Mute check
                for ms, me in mute_intervals:
                    if ms <= t <= me: return audio * 0.0
                
                # Ducking check
                factor = 1.0
                for v_start, v_end in merged_intervals:
                    if v_start <= t <= v_end: factor = duck_ratio; break
                    elif (v_start - att) <= t < v_start:
                        p = (t - (v_start - att)) / att
                        factor = min(factor, 1.0 - (p * (1.0 - duck_ratio)))
                    elif v_end < t <= (v_end + rel):
                        p = (t - v_end) / rel
                        factor = min(factor, duck_ratio + (p * (1.0 - duck_ratio)))
                
                return audio * (cur_peak * factor)

        return apply_global_ducking
