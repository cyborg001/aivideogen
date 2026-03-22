import re

def safe_eval_math(val, default=0.0):
    if val is None: return default
    s = str(val).replace(' ', '').replace(',', '.')
    if not s: return default
    if not re.match(r'^[\d\.\+\-\*\/\(\)]+$', s):
        try: return float(s)
        except: return default
    try:
        return float(eval(s, {"__builtins__": None}, {}))
    except:
        return default

def test_parsing(move_str):
    move_configs = []
    sub_moves = move_str.split('+')
    for sm in sub_moves:
        parts = [p.strip() for p in sm.strip().split(':') if p.strip()]
        if not parts: continue
        mdir = parts[0].upper()
        # The logic in video_engine.py:
        mstart = safe_eval_math(parts[1] if len(parts) > 1 else "50.0", 50.0)
        mend = safe_eval_math(parts[2] if len(parts) > 2 else str(mstart), mstart)
        move_configs.append({'dir': mdir, 'start': mstart, 'end': mend})
    return move_configs

print("Case 'HOR:50':", test_parsing("HOR:50"))
print("Case 'HOR:50:50':", test_parsing("HOR:50:50"))
print("Case 'HOR:50 + VER:30':", test_parsing("HOR:50 + VER:30"))
