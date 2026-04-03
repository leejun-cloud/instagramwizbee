import json
import os
from card_maker_v3 import InstaWizbeeV3

def main():
    project_root = "/Users/ichangjun/Documents/GitHub/insta-wizbee"
    data_file = os.path.join(project_root, "book_data.json")
    output_dir = os.path.join(project_root, "images")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    # Initialize V3 Engine
    v3 = InstaWizbeeV3(project_root)
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    generated_count = 0
    # Target: Apr 3rd to Apr 30th (Day 10 to Day 37)
    for item in data:
        day = item.get('day')
        if day is not None and 10 <= day <= 37:
            title = item.get('book_title', 'Wizbee Wisdom')
            content = item.get('hook', '')
            
            # Sanitize filename
            filename = f"day_{day}.jpg"
            output_path = os.path.join(output_dir, filename)
            
            print(f"Generating Day {day}: {title}...")
            try:
                v3.create_card(title, content, output_path)
                generated_count += 1
            except Exception as e:
                print(f"Error generating Day {day}: {e}")
                
    print(f"\n✅ Batch Generation Complete! Total: {generated_count} images.")
    print(f"Output Directory: {output_dir}")

if __name__ == "__main__":
    main()
