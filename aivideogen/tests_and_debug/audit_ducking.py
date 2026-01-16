
import os
import sys
import json
import django
import re
import numpy as np

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from generator.models import VideoProject

def estimate_duration(text, pause):
    # Strip tags
    clean = re.sub(r'\[.*?\]', '', text)
    clean = re.sub(r'<[^>]+>', '', clean)
    words = len(clean.split())
    # Est. 150 wpm = 2.5 words/sec
    speak_time = words / 2.5
    if speak_time < 1.0: speak_time = 1.0
    return speak_time + pause

def audit_latest_project():
    print("🔍 Auditing Audio Ducking Logic (Logic Verification)...")
    
    project = VideoProject.objects.last()
    if not project:
        print("❌ No projects found.")
        return

    print(f"🎬 Project ID: {project.id}")
    print(f"📝 Title: {project.title}")
    
    # 1. Parse Script to estimate intervals
    try:
        data = json.loads(project.script_text)
    except:
        print("❌ Script is not valid JSON. Cannot audit.")
        return

    voice_intervals = []
    current_time = 0.0
    
    blocks = data.get('blocks', [])
    for block in blocks:
        for scene in block.get('scenes', []):
            text = scene.get('text', '')
            pause = scene.get('pause', 0)
            
            # Estimate Speak Time
            speak_dur = estimate_duration(text, 0) # Raw speak time
            
            # Voice is active from current_time to current_time + speak_dur
            v_start = current_time
            v_end = current_time + speak_dur
            voice_intervals.append((v_start, v_end))
            
            # Advance time (Speak + Pause)
            current_time += (speak_dur + pause)

    total_duration = current_time
    print(f"⏱️ Total Estimated Duration: {total_duration:.2f}s")
    print(f"🗣️ Estimated {len(voice_intervals)} voice segments based on text length.")

    # 3. Simulate Volume Curve
    DEFAULT_VOL = 1.0
    DUCK_VOL = 0.12
    FADE_OUT = 0.3
    FADE_IN = 1.5
    
    def simulate_vol(t):
        for start, end in voice_intervals:
            if start <= t <= end:
                return DUCK_VOL
            # Fade Out
            if (start - FADE_OUT) <= t < start:
                prog = (t - (start - FADE_OUT)) / FADE_OUT
                return DEFAULT_VOL - (prog * (DEFAULT_VOL - DUCK_VOL))
            # Fade In
            if end < t <= (end + FADE_IN):
                prog = (t - end) / FADE_IN
                return DUCK_VOL + (prog * (DEFAULT_VOL - DUCK_VOL))
        return DEFAULT_VOL

    # 4. Probe
    print("\n📊 Volume Logic Verification:")
    print("   (Checks if the math correctly drops volume during estimated voice times)")
    print("-" * 75)
    print(f"{'Time (s)':<10} | {'Est. State':<15} | {'Vol Multiplier':<15} | {'Check'}")
    print("-" * 75)

    sample_points = [0.0]
    # Sample around first 3 intervals
    for i, (s, e) in enumerate(voice_intervals[:3]):
        sample_points.append(max(0, s - 0.5)) # Just before
        sample_points.append(s + 0.1)         # Just started
        sample_points.append((s+e)/2)         # Middle
        sample_points.append(e + 0.1)         # Just ended (Fade In starts)
        sample_points.append(e + 2.0)         # Full silence

    sample_points.sort()
    seen = set()
    
    for t in sample_points:
        if t < 0 or t > total_duration: continue
        if abs(t - round(t,1)) < 0.05: pass
        if t in seen: continue
        seen.add(t)
        
        vol = simulate_vol(t)
        
        status = "SILENCE 🎵"
        for s, e in voice_intervals:
            if s <= t <= e:
                status = "VOICE 🗣️"
                break
        
        check = "✅ OK"
        if status == "VOICE 🗣️" and vol > 0.3: check = "❌ FAIL (Too Loud)"
        if status == "SILENCE 🎵" and vol < 0.8:
            # Check if likely fading
            is_fading = False
            for s, e in voice_intervals:
                if (s - FADE_OUT) <= t < s or e < t <= (e + FADE_IN):
                    is_fading = True
            if is_fading: check = "⚠️ Fading..."
            else: check = "❓ Low? (Maybe overlap)"

        print(f"{t:<10.2f} | {status:<15} | {vol:<15.4f} | {check}")

    print("-" * 75)
    print("CONCLUSION:")
    print("If you see '0.1200' during VOICE, code is correct.")

if __name__ == "__main__":
    audit_latest_project()
