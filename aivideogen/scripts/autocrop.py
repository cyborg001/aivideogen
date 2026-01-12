import sys
from PIL import Image, ImageChops

def autocrop_image(file_path, threshold=240):
    try:
        image = Image.open(file_path).convert("RGBA")
        
        # Convert to numpy to process pixels with threshold
        import numpy as np
        data = np.array(image)
        
        # Determine pixels that are "white" based on threshold (R,G,B all > threshold)
        r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
        white_mask = (r > threshold) & (g > threshold) & (b > threshold)
        
        # Create a mask for non-white areas
        mask = ~white_mask
        
        # Find coordinates of non-white pixels
        coords = np.argwhere(mask)
        
        if coords.size > 0:
            y_min, x_min = coords.min(axis=0)
            y_max, x_max = coords.max(axis=0)
            
            # Crop using these coordinates
            cropped = image.crop((x_min, y_min, x_max + 1, y_max + 1))
            cropped.save(file_path)
            print(f"Successfully cropped {file_path} with threshold {threshold}")
        else:
            print(f"No content found with threshold {threshold}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        autocrop_image(sys.argv[1])
    else:
        print("Usage: python autocrop.py <image_path>")
