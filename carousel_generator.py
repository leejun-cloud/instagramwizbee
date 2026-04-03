import os
import json
import traceback
from create_card_news import generate_card
from style_blueprint import extract_blueprint

DATA_FILE = "book_data.json"

def create_carousel_entry(topic, book_title, slides, caption, hashtags):
    """Adds a carousel entry with multiple slides to the data file."""
    if not os.path.exists(DATA_FILE):
        data = []
    else:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            
    day_num = max([p["day"] for p in data]) + 1 if data else 1
    
    # Store slide texts and their targets
    image_paths = [f"images/carousel_{day_num}_{i+1}.png" for i in range(len(slides))]
    
    entry = {
        "day": day_num,
        "type": "carousel",
        "book_title": book_title,
        "topic": topic,
        "slides": slides, # List of strings for each slide
        "hook": slides[0], # Use first slide as hook
        "caption": caption,
        "hashtags": hashtags,
        "image_paths": image_paths,
        "approved": False, # Manual approval needed
        "published": False
    }
    
    data.append(entry)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return entry

def generate_carousel_images(day_num, slides, image_paths):
    """Generates 5 images based on the slide texts and reference style."""
    ref_dir = "references"
    reference_images = [os.path.join(ref_dir, f) for f in os.listdir(ref_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))] if os.path.exists(ref_dir) else []
    
    style_params = None
    if reference_images:
        ref_image = reference_images[day_num % len(reference_images)]
        print(f"🎨 Carousel Style Analysis: {ref_image}")
        style_params = extract_blueprint(ref_image)

    for i, slide_text in enumerate(slides):
        target_path = image_paths[i]
        print(f"📸 Generating Slide {i+1}: {target_path}")
        try:
            generate_card(slide_text, target_path, style_params=style_params)
        except Exception as e:
            print(f"Error on slide {i+1}: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    # This script will be called with arguments or manually updated for now
    print("Carousel Generator Loaded. Use create_carousel_entry to add new units.")
