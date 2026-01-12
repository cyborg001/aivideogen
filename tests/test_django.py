import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
print("Initializing Django...")
django.setup()
print("Django initialized successfully.")
