from generator.models import VideoProject
lines = []
for p in VideoProject.objects.all().order_by('-id')[:20]:
    hw, dur, res = '', '', ''
    for l in (p.log_output or '').split('\n'):
        if '[HW]' in l: hw = l
        if 'FASE 1' in l: dur = l
        if 'Iniciando render' in l: res = l
    lines.append(f"ID {p.id} | Vid: {p.duration}s | HW: {hw[-18:]} | Time: {dur} | Res: {res[-12:]}")

open('query_out.txt', 'w', encoding='utf-8').write('\n'.join(lines))
