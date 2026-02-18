
import os, sys, time, asyncio
from generator.models import VideoProject
from generator.avgl_engine import parse_avgl_json, generate_audio_edge

def run_benchmark():
    try:
        project = VideoProject.objects.get(id=63)
        print(f"Project: {project.title}")
        print(f"Engine: {project.engine}")
        print(f"Voice ID: {project.voice_id}")
        
        script = parse_avgl_json(project.script_text)
        scenes = script.get_all_scenes()
        print(f"Scenes: {len(scenes)}")

        async def test_audio():
            start = time.time()
            for i, scene in enumerate(scenes):
                if not scene.text: continue
                text = scene.text
                voice = project.voice_id if project.voice_id else (scene.voice or "es-DO-EmilioNeural")
                
                print(f"Scene {i+1}: Gen audio ({len(text)} chars) using {voice}...")
                t0 = time.time()
                # Dummy path
                out = f"temp_debug_audio_{i}.mp3"
                
                # Mock Rate if not present
                rate = "+0%"
                
                try:
                    await generate_audio_edge(text, out, voice=voice, rate=rate)
                    dt = time.time() - t0
                    size = os.path.getsize(out) if os.path.exists(out) else 0
                    print(f"  Done in {dt:.2f}s | Size: {size} bytes")
                except Exception as e:
                    print(f"  FAILED: {e}")
                
                if os.path.exists(out): os.remove(out)
            
            total = time.time() - start
            print(f"Total Audio Gen Time: {total:.2f}s")
            
            if total > 60:
                print("DIAGNOSIS: AUDIO IS SLOW. Check Network or Edge API.")
            else:
                print("DIAGNOSIS: AUDIO IS FAST. Problem is likely Video Encoding or Assets.")

        asyncio.run(test_audio())
        
    except Exception as e:
        print(f"Benchmark Error: {e}")

run_benchmark()
