import os
from moviepy import VideoFileClip, AudioFileClip

video_stream = r'c:\Users\hp\aivideogen\aivideogen\media\assets\trump_speeches\trump_nato_hormuz.f398.mp4'
audio_stream = r'c:\Users\hp\aivideogen\aivideogen\media\assets\trump_speeches\trump_nato_hormuz.f251.webm'
output_file = r'c:\Users\hp\aivideogen\aivideogen\media\assets\trump_speeches\trump_nato_hormuz_merged.mp4'

def merge():
    if not os.path.exists(video_stream) or not os.path.exists(audio_stream):
        print("Streams not found.")
        return

    print(f"Merging {os.path.basename(video_stream)} and {os.path.basename(audio_stream)}...")
    v_clip = VideoFileClip(video_stream)
    a_clip = AudioFileClip(audio_stream)
    
    final_clip = v_clip.with_audio(a_clip)
    final_clip.write_videofile(output_file, codec="libx264", audio_codec="aac")
    
    v_clip.close()
    a_clip.close()
    print(f"Success! Merged file saved to: {output_file}")

if __name__ == "__main__":
    merge()
