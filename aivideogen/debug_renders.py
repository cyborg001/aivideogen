import os, sys, django
sys.path.insert(0, r'c:\Users\hp\aivideogen')
sys.path.insert(0, r'c:\Users\hp\aivideogen\aivideogen')
os.environ['DJANGO_SETTINGS_MODULE'] = 'aivideogen.settings'
django.setup()
from generator.models import VideoProject
for p in VideoProject.objects.all().order_by('-id')[:10]:
    log = p.log_output or ''
    hw = next((l for l in log.split('\n') if '[HW]' in l), '')
    dur = next((l for l in log.split('\n') if 'FASE 1' in l), '')
    res = next((l for l in log.split('\n') if 'Iniciando render' in l), '')
    print(f"ID {p.id} | Mode: {p.render_mode} | Vid: {p.duration}s | HW: {hw[-18:]} | Time: {dur} | Res: {res[-12:]}")
