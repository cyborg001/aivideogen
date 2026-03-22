import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def test_translation():
    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash-latest")
    
    print(f"API KEY detectada: {'***' + api_key[-4:] if api_key else 'NO ENCONTRADA'}")
    print(f"Modelo: {model_name}")
    
    if not api_key:
        return
        
    text = "Hola Arquitecto, esto es una prueba de traducción."
    target_lang = "en"
    lang_name = "Inglés"
    
    prompt = f"Traduce el siguiente texto al {lang_name}. NO agregues explicaciones, solo devuelve el texto traducido.\n\nTEXTO:\n{text}"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            content = result['candidates'][0]['content']['parts'][0]['text']
            print(f"ORIGINAL: {text}")
            print(f"TRADUCIDO: {content.strip()}")
        else:
            print(f"ERROR: {response.text}")
    except Exception as e:
        print(f"EXCEPCIÓN: {str(e)}")

if __name__ == "__main__":
    test_translation()
