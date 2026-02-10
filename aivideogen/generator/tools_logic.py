import os
import logging
from moviepy import ImageClip, concatenate_videoclips
from django.conf import settings

logger = logging.getLogger(__name__)

def create_image_carousel_mp4(image_paths, output_path, total_duration=5.0):
    """
    v15.9.2: Creates a single MP4 video from a list of image paths.
    
    Args:
        image_paths (list): List of absolute paths to images.
        output_path (str): Full path to save the resulting .mp4.
        total_duration (float): Total duration of the resulting video in seconds.
        
    Returns:
        tuple: (success, message)
    """
    try:
        if not image_paths:
            return False, "No se proporcionaron imágenes."

        # Calculate duration per image
        num_images = len(image_paths)
        duration_per_image = float(total_duration) / num_images
        
        # Verify all paths exist
        valid_paths = [p for p in image_paths if os.path.exists(p)]
        if not valid_paths:
            return False, "Ninguna de las rutas de imagen proporcionadas es válida."

        logger.info(f"[Carousel] Creando video con {len(valid_paths)} imágenes. Duración por imagen: {duration_per_image:.2f}s")
        
        # v15.9.5: Use ImageClip + concatenate_videoclips(method="compose")
        # This handles different image sizes by centering them on a black background
        clips = []
        for p in valid_paths:
            try:
                # v15.9.6: MoviePy v2.0+ uses with_duration, v1.0 uses set_duration.
                # We try both to be safe and avoid the 'attribute not found' error.
                img_clip = ImageClip(p)
                
                if hasattr(img_clip, 'with_duration'):
                    img_clip = img_clip.with_duration(duration_per_image)
                else:
                    img_clip = img_clip.set_duration(duration_per_image)
                
                clips.append(img_clip)
            except Exception as e:
                logger.error(f"[Carousel] Error cargando imagen {p}: {str(e)}")

        if not clips:
            return False, "No se pudieron cargar las imágenes."

        # method="compose" is the key to handling different sizes
        final_clip = concatenate_videoclips(clips, method="compose")
        
        # v15.9.7: CRITICAL for Windows/yuv420p: Ensure dimensions are even
        # If width or height is odd, ffmpeg with yuv420p will FAIL.
        w, h = final_clip.size
        new_w = w if w % 2 == 0 else w - 1
        new_h = h if h % 2 == 0 else h - 1
        # v15.9.10: CONSOLIDATED: Move all specific flags to ffmpeg_params 
        # to avoid "unexpected keyword argument" in different MoviePy versions.
        ffmpeg_params = [
            "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", # Even dimensions
            "-pix_fmt", "yuv420p"                      # Windows compatibility
        ]

        logger.info(f"[Carousel] Renderizando video final: {output_path}")

        # v15.9.10: Use minimal keywords for maximum robustness
        final_clip.write_videofile(
            output_path, 
            codec="libx264", 
            audio=False, 
            fps=24, 
            ffmpeg_params=ffmpeg_params
        )
        
        # Close clips to free resources
        for c in clips:
            c.close()
        final_clip.close()
        
        return True, f"Video creado exitosamente en: {output_path}"

    except Exception as e:
        logger.error(f"[Carousel] Error fatal: {str(e)}")
        return False, f"Error durante el procesamiento: {str(e)}"
