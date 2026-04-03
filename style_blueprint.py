import os
import random
from PIL import Image, ImageStat

def extract_blueprint(sample_path):
    """
    Analyzes a sample image to extract design parameters.
    Returns a dictionary of StyleParams.
    """
    if not os.path.exists(sample_path):
        return None
        
    try:
        img = Image.open(sample_path).convert('RGB')
        width, height = img.size
        
        # Sample points for colors (9-point grid)
        points = [
            (10, 10), (width//2, 10), (width-10, 10),
            (10, height//2), (width//2, height//2), (width-10, height//2),
            (10, height-10), (width//2, height-10), (width-10, height-10)
        ]
        
        colors = [img.getpixel(p) for p in points]
        
        # Detect gradient or solid
        # bg_top: average of top 3 points
        # bg_bottom: average of bottom 3 points
        bg_top = tuple(sum(colors[i][j] for i in range(3)) // 3 for j in range(3))
        bg_bottom = tuple(sum(colors[i+6][j] for i in range(3)) // 3 for j in range(3))
        
        # Determine text color (contrast test)
        center_color = colors[4]
        brightness = sum(center_color) / 3
        text_color = (20, 20, 20) if brightness > 128 else (255, 230, 180) # Dark for light bg, Champagne for dark
        
        # Apply 5% variation logic
        bg_top = apply_variation(bg_top, 0.05)
        bg_bottom = apply_variation(bg_bottom, 0.05)
        
        return {
            "bg_top": bg_top,
            "bg_bottom": bg_bottom,
            "text_color": text_color,
            "has_gradient": True # Assume gradient for premium look
        }
        
    except Exception as e:
        print(f"Error analyzing style from {sample_path}: {e}")
        return None

def apply_variation(color, amount):
    """Applies a small random variation to an RGB tuple."""
    return tuple(max(0, min(255, int(c * (1 + random.uniform(-amount, amount))))) for c in color)

if __name__ == "__main__":
    # Test with a dummy if needed
    print("Style Blueprint Engine initialized.")
