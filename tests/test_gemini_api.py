import os
import requests
from dotenv import load_dotenv

def test_gemini():
    # Load .env relative to this script location
    env_path = os.path.join(os.getcwd(), '.env')
    load_dotenv(env_path)
    
    api_key = os.getenv("GEMINI_API_KEY")
    # Probar nombres comunes de modelos
    models_to_try = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-pro"
    ]
    
    print(f"--- Diagnóstico Gemini ---")
    
    if not api_key:
        print("❌ ERROR: No se encontró GEMINI_API_KEY en el archivo .env")
        return

    print(f"Status: Clave detectada (longitud: {len(api_key)})")
    
    print(f"\n--- Listando modelos disponibles ---")
    list_url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
    try:
        list_response = requests.get(list_url, timeout=10)
        if list_response.status_code == 200:
            models = list_response.json().get('models', [])
            for m in models:
                print(f"[MODELO]: {m['name']}")
        else:
            print(f"[FAIL] Error al listar modelos: {list_response.status_code}")
            # print(f"Detalle: {list_response.text}")
    except Exception as e:
        print(f"[FAIL] Error de conexion al listar: {str(e)}")

    print(f"\n--- Probando Generacion ---")
    for model_name in models_to_try:
        full_model_name = model_name if "/" in model_name else f"models/{model_name}"
        print(f"\nProbando: {full_model_name}...")
        url = f"https://generativelanguage.googleapis.com/v1/{full_model_name}:generateContent?key={api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": "OK"}]
            }]
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                print(f"[OK] {full_model_name} funciona.")
                print(f"Respuesta: {response.json()['candidates'][0]['content']['parts'][0]['text'].strip()}")
            else:
                print(f"[FAIL] ({full_model_name}): {response.status_code}")
        except Exception as e:
            print(f"[FAIL] Error de Conexion ({full_model_name}): {str(e)}")

if __name__ == "__main__":
    test_gemini()
