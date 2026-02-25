import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import YouTubeToken

def check_tokens():
    tokens = YouTubeToken.objects.all()
    if not tokens:
        print("❌ No se encontraron tokens de YouTube en la base de datos.")
        return
    
    for i, token in enumerate(tokens):
        print(f"\n--- Token {i+1} ---")
        # El token suele tener estructura JSON con campos de Google OAuth
        token_data = token.token
        print(f"ID del Cliente: {token_data.get('client_id', 'N/A')}")
        print(f"Scopes: {token_data.get('scopes', 'N/A')}")
        # El correo no siempre está en el token de acceso, pero a veces está en los metadatos o podemos inferirlo
        # Si no está, al menos sabemos que hay un token activo.
        print("Estado del Token: Activo" if not token_data.get('expired') else "Estado del Token: Expirado")

if __name__ == "__main__":
    check_tokens()
