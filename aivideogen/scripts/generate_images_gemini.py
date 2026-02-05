import os
import requests
import json
import base64
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
# Probaremos con gemini-3-pro-image-preview
MODEL_NAME = "models/gemini-3-pro-image-preview" 

def generate_image_content(prompt, output_filename):
    if not API_KEY or API_KEY == "tu_api_key_aqui":
        print("Error: GEMINI_API_KEY no configurada.")
        return False

    # Endpoint para generateContent (el estandar)
    url = f"https://generativelanguage.googleapis.com/v1beta/{MODEL_NAME}:generateContent?key={API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    headers = {'Content-Type': 'application/json'}
    
    print(f"Generando (content): {output_filename}...")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        if response.status_code == 200:
            result = response.json()
            # Estructura de respuesta de gemini-2.0-flash-exp-image-generation:
            # candidates[0].content.parts[0].inlineData.data
            if 'candidates' in result and len(result['candidates']) > 0:
                parts = result['candidates'][0]['content']['parts']
                for part in parts:
                    if 'inlineData' in part:
                        image_data = base64.b64decode(part['inlineData']['data'])
                        with open(output_filename, 'wb') as f:
                            f.write(image_data)
                        print(f"¡Éxito! Imagen guardada.")
                        return True
            print(f"Error: No se encontró data de imagen en la respuesta.")
            print(json.dumps(result, indent=2))
        else:
            print(f"Error de API Gemini ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")
    return False

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "media", "assets")
    os.makedirs(output_dir, exist_ok=True)

    prompts = [
        {"name": "musk_spacex_xai.png", "prompt": "Cinematic photorealistic shot of Elon Musk in front of a giant holographic merger logo of SpaceX and xAI. High-tech lab background, blue and silver color palette, 8k resolution, cinematic lighting."},
        {"name": "apple_google_siri.png", "prompt": "Modern smartphone held in a hand showing a futuristic Siri interface merged with the Google Gemini logo. Soft ethereal purple and blue gradients, high-end product photography, minimalist design, Apple style."},
        {"name": "google_genie_world.png", "prompt": "A person wearing a minimalist VR headset, pointing at a floating virtual world being built in real-time. Text prompts appearing in front of them, morphing into a detailed 3D forest environment. Cyberpunk aesthetic, clean, magical realism tech."},
        {"name": "waymo_tokyo.png", "prompt": "A sleek, white Waymo autonomous vehicle driving through a futuristic Tokyo street at night. Neon lights reflecting on the car's body, people walking by, 8k resolution, cinematic lighting, cyberpunk city."},
        {"name": "ai_coworker.png", "prompt": "A split-screen view: on one side a person in a home office, on the other side a glowing digital AI assistant pointing at a holographic task board. Collaborative atmosphere, warm lighting, premium look."}
    ]

    for p in prompts:
        output_path = os.path.join(output_dir, p["name"])
        if not os.path.exists(output_path):
            generate_image_content(p["prompt"], output_path)
        else:
            print(f"Saltando {p['name']}, ya existe.")

if __name__ == "__main__":
    main()
