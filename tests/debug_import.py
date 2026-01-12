print("Importing os...")
import os
print("Importing django...")
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
print("Django setup...")
django.setup()
print("Importing models...")
from generator.models import VideoProject
print("Importing utils...")
from generator import utils
print("Importing views...")
from generator import views
print("Done.")
