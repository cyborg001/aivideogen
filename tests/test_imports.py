import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
print("Django setup done. Importing views...")
try:
    from generator import views
    print("Views imported successfully.")
except Exception as e:
    print(f"Error importing views: {e}")
