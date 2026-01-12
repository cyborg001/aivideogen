from PIL import Image, ImageDraw, ImageFont

def create_placeholder(filename, text, color):
    img = Image.new('RGB', (1920, 1080), color=color)
    d = ImageDraw.Draw(img)
    try:
        # Try to use a default font
        font = ImageFont.truetype("arial.ttf", 80)
    except:
        font = ImageFont.load_default()
    
    # Calculate text position (rough centering)
    d.text((960, 540), text, fill=(255, 255, 255), anchor="mm")
    
    img.save(f"media/assets/{filename}")
    print(f"Created {filename}")

if __name__ == "__main__":
    import os
    os.makedirs("media/assets", exist_ok=True)
    create_placeholder("default_bg.png", "IMAGEN POR DEFECTO", (20, 20, 80))
    create_placeholder("placeholder_tech.jpg", "FALTA IMAGEN", (0, 50, 0))
