import re

def extract_subtitles_v35(text):
    """
    Extracts subtitles from tags. Preserves the text for the narrator.
    v6.8: Robust Mapping Logic. Eliminates repetition and silence bugs.
    """
    wrapped_pattern = re.compile(r'\[\s*SUB\s*\](.*?)\s*\[\s*/SUB\s*\]', re.IGNORECASE | re.DOTALL)
    simple_pattern = re.compile(r'\[\s*SUB\s*:\s*(.*?)\s*\]', re.IGNORECASE)
    
    tags = []
    for m in wrapped_pattern.finditer(text):
        tags.append({'start': m.start(), 'end': m.end(), 'content': m.group(1).strip(), 'type': 'wrapped'})
    for m in simple_pattern.finditer(text):
        if not any(t['start'] <= m.start() < t['end'] for t in tags):
            tags.append({'start': m.start(), 'end': m.end(), 'content': m.group(1).strip(), 'type': 'simple'})
            
    tags.sort(key=lambda x: x['start'])
    
    last_idx = 0
    raw_subs = []
    current_clean_text = ""
    
    for tag in tags:
        before = text[last_idx:tag['start']]
        current_clean_text += before
        
        word_offset = len(current_clean_text.split())
        
        content = tag['content']
        display_text = content
        word_count = 3
        
        if tag['type'] == 'simple' and '|' in content:
            parts = [p.strip() for p in content.split('|')]
            try:
                word_count = int(parts[0])
                display_text = parts[1] if len(parts) > 1 else ""
            except:
                display_text = parts[0]
        else:
            word_count = len(display_text.split())
            if word_count < 2: word_count = 3
            
        raw_subs.append({"text": display_text, "offset": word_offset, "word_count": word_count})
        current_clean_text += display_text
        last_idx = tag['end']
        
    current_clean_text += text[last_idx:]
    clean_text = re.sub(r'\[\s*/?SUB\s*(?::.*?)?\]', '', current_clean_text, flags=re.IGNORECASE)
    
    return clean_text.strip(), raw_subs

# Test cases
test1 = "Hola [SUB]primer subtitulo[/SUB] mas [SUB]segundo subtitulo[/SUB]."
test2 = "[SUB]Primero[/SUB] y luego [SUB]Segundo[/SUB]"

for t in [test1, test2]:
    c, s = extract_subtitles_v35(t)
    print(f"Original: {t}")
    print(f"Clean   : {c}")
    print(f"Subs    : {s}\n")
