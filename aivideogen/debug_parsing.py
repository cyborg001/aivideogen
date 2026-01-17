from generator.avgl_engine import convert_text_to_avgl_json
import json

line = "Gancho: La Esfera | sphere_las_vegas.png | ZOOM_IN:1.0:1.3 + OVERLAY:dust | Bienvenidos a Noticias de IA y ciencias. | 1.5"
try:
    data = convert_text_to_avgl_json(line)
    print(json.dumps(data, indent=2))
    
    # Simulate extraction
    asset = data['blocks'][0]['scenes'][0]['assets'][0]
    print(f"Asset Zoom: {asset.get('zoom')}")
    print(f"Asset Move: {asset.get('move')}")
    print(f"Asset Overlay: {asset.get('overlay')}")
    
    # Simulate float conversion check
    if asset.get('zoom'):
        parts = asset['zoom'].split(':')
        print(f"Zoom floats: {float(parts[0])}, {float(parts[1])}")

except Exception as e:
    print(f"ERROR: {e}")
