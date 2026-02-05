import os
import django
import sys
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import google.oauth2.credentials

# Agregar el directorio del proyecto a sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from generator.models import YouTubeToken
from django.conf import settings

def get_drive_service():
    token_obj = YouTubeToken.objects.last()
    if not token_obj:
        print("Error: No se encontró token de YouTube/Google. Por favor, autoriza la app en la web.")
        return None
    
    credentials = google.oauth2.credentials.Credentials(**token_obj.token)
    return build('drive', 'v3', credentials=credentials)

def upload_file(service, file_path, folder_id=None):
    file_name = os.path.basename(file_path)
    file_metadata = {'name': file_name}
    if folder_id:
        file_metadata['parents'] = [folder_id]
        
    media = MediaFileUpload(file_path, resumable=True)
    
    # Buscar si el archivo ya existe
    query = f"name = '{file_name}'"
    if folder_id:
        query += f" and '{folder_id}' in parents"
    
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    existing_files = results.get('files', [])
    
    if existing_files:
        file_id = existing_files[0]['id']
        print(f"Actualizando: {file_name} ({file_id})")
        return service.files().update(fileId=file_id, media_body=media).execute()
    else:
        print(f"Subiendo nuevo: {file_name}")
        return service.files().create(body=file_metadata, media_body=media, fields='id').execute()

def sync_folder(service, local_path, folder_name, parent_folder_id=None):
    # Crear o buscar carpeta de destino
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder'"
    if parent_folder_id:
        query += f" and '{parent_folder_id}' in parents"
    
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    folders = results.get('files', [])
    
    if folders:
        folder_id = folders[0]['id']
    else:
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]
        folder = service.files().create(body=file_metadata, fields='id').execute()
        folder_id = folder.get('id')
        print(f"Carpeta creada: {folder_name} (ID: {folder_id})")

    for root, dirs, files in os.walk(local_path):
        for file in files:
            # Ignorar archivos ocultos o de sistema
            if file.startswith('.') or file == 'db.sqlite3':
                continue
            full_path = os.path.join(root, file)
            # Mantener estructura de subcarpetas (simplificado para este script)
            upload_file(service, full_path, folder_id)

def main():
    service = get_drive_service()
    if not service:
        return

    # 1. Sincronizar Reglas (.agent/workflows)
    workflows_path = os.path.join(os.path.dirname(settings.BASE_DIR), '.agent', 'workflows')
    if os.path.exists(workflows_path):
        print("Sincronizando Reglas (.agent/workflows)...")
        sync_folder(service, workflows_path, "NotiNews_Reglas_Agent")

    # 2. Sincronizar Memoria (brain/)
    # La memoria está en AppData\..\brain\<conv-id>
    # Intentaremos subir la carpeta de esta conversación específicamente
    # path: C:\Users\cgrs8\.gemini\antigravity\brain\6e478669-79a3-4721-bad7-856c0404e2d9
    brain_path = r"C:\Users\cgrs8\.gemini\antigravity\brain\6e478669-79a3-4721-bad7-856c0404e2d9"
    if os.path.exists(brain_path):
        print(f"Sincronizando Memoria (brain)...")
        sync_folder(service, brain_path, "NotiNews_Memoria_AI")

if __name__ == "__main__":
    main()
