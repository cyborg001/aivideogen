
import re

def test_split():
    text = "[SUB: La Saga Alpha][TENSO]Sabías que Google ya no solo juega ajedrez... [/TENSO]"
    
    # Simple versions of the logic in avgl_engine.py
    pattern = r'(\[PAUSA:[\d\.]+\]|\[(?:TENSO|EPICO|SUSPENSO|GRITANDO|SUSURRO)\].*?\[/(?:TENSO|EPICO|SUSPENSO|GRITANDO|SUSURRO)\])'
    parts = re.split(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    
    print(f"Parts: {parts}")
    
    segments = []
    for part in parts:
        if not part: continue
        
        pause_match = re.match(r'\[PAUSA:([\d\.]+)\]', part, re.IGNORECASE)
        if pause_match:
            segments.append(('pause', float(pause_match.group(1))))
            continue
            
        emo_match = re.match(r'\[(TENSO|EPICO|SUSPENSO|GRITANDO|SUSURRO)\](.*?)\[/\1\]', part, re.IGNORECASE | re.DOTALL)
        if emo_match:
            emo_text = emo_match.group(2).strip()
            segments.append(('emo', emo_text))
            continue
            
        clean_text = re.sub(r'\[.*?\]', '', part).strip()
        if clean_text:
            segments.append(('text', clean_text))
            
    print(f"Segments: {segments}")

if __name__ == "__main__":
    test_split()
