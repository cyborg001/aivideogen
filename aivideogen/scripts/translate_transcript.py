import os
import json
import requests
import sys
from dotenv import load_dotenv

# Cargar variables de entorno desde .env en la raíz del proyecto
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def translate_with_gemini(transcript_text):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[-] Error: GEMINI_API_KEY no configurada.")
        return None

    prompt = f"""
Eres un editor experto en YouTube Shorts y traductor de discursos de alto impacto. 
Tu objetivo es transformar el siguiente transcript de Donald Trump (inglés) en un guion para un Short en español sincronizado.

TRANSCRIPT ORIGINAL CON TIMESTAMPS:
{transcript_text}

INSTRUCCIONES DE TRADUCCIÓN:
1. Selecciona los mejores 58-60 segundos del discurso. Deben ser las partes más directas y polémicas sobre la OTAN.
2. Tradúcelo al español con un estilo "FrankProducer".
3. IMPORTANTE: Cada fragmento del guion DEBE incluir el "start_time" y "end_time" aproximado del video original (según los datos arriba) para que yo sepa qué parte del video usar.
4. El formato de salida debe ser un JSON compatible con el motor AVGL v5.0.

FORMATO DEL JSON:
{{
  "title": "TRUMP_NATO_REBELION",
  "config": {{ "voice": "es-US-AlonsoNeural", "rate": "+5%", "lipsync": true }},
  "script": [
    {{ 
      "start_time": 86.28, 
      "end_time": 94.52, 
      "text": "Bienvenidos a la rebelión. Donald Trump acaba de soltar la bomba sobre la OTAN." 
    }},
    ...
  ]
}}
Responde ÚNICAMENTE con el objeto JSON.
"""

    model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-flash-latest")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"response_mime_type": "application/json"}
    }

    try:
        response = requests.post(url, json=payload, timeout=60)
        if response.status_code == 200:
            result = response.json()
            content = result['candidates'][0]['content']['parts'][0]['text']
            return json.loads(content)
        else:
            print(f"[-] Error API Gemini: {response.status_code}")
            return None
    except Exception as e:
        print(f"[-] Error en traducción: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python translate_transcript.py <transcript_json>")
        sys.exit(1)

    file_path = sys.argv[1]
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Extraer segmentos relevantes (solo los primeros para no exceder tokens, o filtrar por Trump)
    segments = data.get("segments", [])
    formatted_segments = ""
    for s in segments[:300]: # Limitar a los primeros 300 segmentos (~10-15 mins)
        formatted_segments += f"[{s['start']:.2f} - {s['end']:.2f}]: {s['text']}\n"
    
    print("[*] Enviando segmentos a Gemini para traducción adaptativa...")
    translated_script = translate_with_gemini(formatted_segments)
    
    if translated_script:
        out_file = file_path.replace("_transcript.json", "_translated_avgl.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(translated_script, f, indent=4, ensure_ascii=False)
        print(f"[+] Guion traducido generado: {out_file}")
    else:
        print("[-] Falló la traducción.")
