import json
import os
import datetime
from card_maker_v3_premium import InstaWizbeePremium

def main():
    project_root = "/Users/ichangjun/Documents/GitHub/insta-wizbee"
    data_file = os.path.join(project_root, "book_data.json")
    output_dir = os.path.join(project_root, "images")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Initialize Premium V3 Engine
    premium = InstaWizbeePremium(project_root)
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    print(f"🚀 [PREMIUM-BATCH] Starting 10-day generation from {today}...")
    
    # Target: 10 days starting from Day 11 (2026-04-04)
    # Day 11 to Day 20
    generated_count = 0
    for item in data:
        day = item.get('day')
        if day is not None and 11 <= day <= 20:
            title = item.get('book_title', 'Wizbee Wisdom')
            # Use Hook for premium cards
            content = item.get('hook', '')
            
            filename = f"day_{day}.jpg"
            output_path = os.path.join(output_dir, filename)
            
            print(f"✨ Generating Premium Day {day}: {title}...")
            try:
                premium.create_premium_card(title, content, day, output_path)
                generated_count += 1
            except Exception as e:
                print(f"Error on Day {day}: {e}")
                
    print(f"\n✅ Premium Batch Complete! Total: {generated_count} images.")
    print(f"Check the 'images/' folder for the results.")

if __name__ == "__main__":
    main()
