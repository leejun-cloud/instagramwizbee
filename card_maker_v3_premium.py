import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

class InstaWizbeePremium:
    """
    Universal Premium Card News Engine (V3 Premium)
    - Supports AI backgrounds with Glassmorphism overlay.
    - Fallback to handcrafted PIL-drawn premium backgrounds (V2 style).
    - Dynamic layout and contrast-aware typography.
    """
    def __init__(self, project_root="/Users/ichangjun/Documents/GitHub/insta-wizbee"):
        self.project_root = project_root
        self.assets_dir = os.path.join(project_root, "assets")
        self.bg_dir = os.path.join(self.assets_dir, "premium_bg")
        self.font_dir = os.path.join(self.assets_dir, "fonts")
        self.width, self.height = 1080, 1080
        
        # System Fonts for macOS (Robust Fallback for Korean)
        self.system_font_paths = [
            "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
            "/System/Library/Fonts/AppleSDGothicNeo.ttc",
            "/System/Library/Fonts/PingFang.ttc"
        ]
        
        # Ensure directories exist
        os.makedirs(self.bg_dir, exist_ok=True)

    def select_font(self, font_name="NanumBrushScript.ttf", size=85):
        # 1. Try specified font
        font_path = os.path.join(self.font_dir, font_name)
        if os.path.exists(font_path) and os.path.getsize(font_path) > 1024:
            try:
                return ImageFont.truetype(font_path, size)
            except: pass
            
        # 2. Robust System Fallback for Mac
        for sys_path in self.system_font_paths:
            if os.path.exists(sys_path):
                return ImageFont.truetype(sys_path, size)
                
        # 3. Final Default
        return ImageFont.load_default()

    def get_text_size(self, draw, text, font):
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    def draw_glassmorphism_card(self, img, box_coords, opacity=180):
        """Draws a semi-transparent blurred white card for premium text readability."""
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw_ov = ImageDraw.Draw(overlay)
        # Rounded rectangle for the card
        draw_ov.rounded_rectangle(box_coords, radius=40, fill=(255, 255, 255, opacity))
        
        # Subtle shadow/border
        draw_ov.rounded_rectangle(box_coords, radius=40, outline=(255, 255, 255, 50), width=2)
        
        return Image.alpha_composite(img, overlay)

    def wrap_text(self, text, font, max_width):
        lines = []
        words = text.split(' ')
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            w = font.getlength(test_line) if hasattr(font, 'getlength') else 0
            if w <= max_width:
                current_line = test_line
            else:
                if current_line: lines.append(current_line)
                current_line = word
        if current_line: lines.append(current_line)
        return lines

    def create_premium_card(self, title, content, day_num, output_path):
        # 1. Background Selection (Priority: AI Illustration > Fallback)
        bg_path = os.path.join(self.bg_dir, f"day_{day_num}.png")
        if os.path.exists(bg_path):
            img = Image.open(bg_path).convert("RGBA")
            img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
            mode = "ILLUSTRATION"
        else:
            # --- Dynamic Generative Premium Drawing (The "Engine" draws) ---
            # 1. Select a Palette based on Day Number
            palettes = [
                {"bg": (252, 250, 245), "accents": [(200, 230, 255, 100), (255, 230, 200, 100), (230, 255, 200, 100)]}, # Soft Pastel
                {"bg": (245, 245, 250), "accents": [(255, 200, 200, 80), (200, 200, 255, 80), (255, 255, 220, 80)]}, # Cool Modern
                {"bg": (255, 252, 240), "accents": [(150, 100, 50, 40), (200, 150, 100, 40), (250, 230, 180, 40)]}, # Earthy/Sepia
                {"bg": (240, 248, 255), "accents": [(100, 149, 237, 60), (0, 191, 255, 60), (176, 224, 230, 60)]}, # Sky/Blue
                {"bg": (255, 245, 245), "accents": [(255, 182, 193, 80), (219, 112, 147, 60), (255, 228, 225, 80)]}, # Rose/Pink
            ]
            palette = palettes[day_num % len(palettes)]
            
            img = Image.new("RGBA", (self.width, self.height), palette["bg"] + (255,))
            draw = ImageDraw.Draw(img)
            
            # 2. Draw Randomized Organic Shapes (Generative Art)
            random.seed(day_num * 100) # Deterministic for each day
            for _ in range(random.randint(4, 7)):
                r = random.randint(300, 800)
                x = random.randint(-200, self.width)
                y = random.randint(-200, self.height)
                color = random.choice(palette["accents"])
                draw.ellipse([x, y, x+r, y+r], fill=color)
            
            # Apply a moderate blur to make it look like a smooth wash/gradient
            img = img.filter(ImageFilter.GaussianBlur(radius=45))
            mode = "GENERATIVE"

        # 2. Composition (Layout & Typography)
        # Illustration & Generative mode use the Glassmorphism card
        if mode in ["ILLUSTRATION", "GENERATIVE"]:
            box_width = 900
            box_height = 550
            x1 = (self.width - box_width) // 2
            
            # Vary Y position slightly based on day for variety
            y_offset = (day_num % 3) * 40
            y1 = (self.height - box_height) // 2 + 30 + y_offset
            
            # Use higher opacity for better contrast
            img = self.draw_glassmorphism_card(img, [x1, y1, x1+box_width, y1+box_height], opacity=235)
            text_color = (25, 25, 25) # Darker for better visibility
            # Deep Bronze/Emerald colors
            title_colors = [(120, 90, 40), (40, 80, 120), (80, 40, 120), (40, 100, 60)]
            title_color = title_colors[day_num % len(title_colors)]
            startY = y1 + 180
        else:
            text_color = (30, 30, 30)
            title_color = (100, 100, 100)
            startY = 450

        draw = ImageDraw.Draw(img)
        
        # 3. Fonts
        try:
            title_font = self.select_font("NanumBrushScript.ttf", 95)
            content_font = self.select_font("NanumPenScript.ttf", 55)
            brand_font = self.select_font(size=24)
        except:
            title_font = ImageFont.load_default()
            content_font = ImageFont.load_default()
            brand_font = ImageFont.load_default()

        # 4. Draw Title
        tw, th = self.get_text_size(draw, title, title_font)
        if mode == "ILLUSTRATION":
            draw.text(((self.width - tw) / 2, y1 + 60), title, font=title_font, fill=title_color)
            startY = y1 + 180
        else:
            draw.text(((self.width - tw) / 2, 300), title, font=title_font, fill=title_color)
            startY = 450

        # 5. Draw Content (Wrapped)
        lines = self.wrap_text(content, content_font, 800)
        curr_y = startY
        for line in lines:
            lw, lh = self.get_text_size(draw, line, content_font)
            draw.text(((self.width - lw) / 2, curr_y), line, font=content_font, fill=text_color)
            curr_y += lh + 25

        # 6. Branding (V2 Style)
        brand_name = "품성독서"
        bw, bh = self.get_text_size(draw, brand_name, brand_font)
        draw.text((self.width - bw - 60, self.height - 80), brand_name, font=brand_font, fill=(150, 150, 150))

        # Save Final Result
        final_img = img.convert("RGB")
        final_img.save(output_path, "JPEG", quality=95)
        return output_path

if __name__ == "__main__":
    premium = InstaWizbeePremium()
    # Test Generation
    premium.create_premium_card(
        "테스트 타이틀", 
        "이것은 Premium V3 엔진의 테스트 결과물입니다. 글래스모피즘과 캘리그라피가 조화를 이룹니다.", 
        11, 
        "/Users/ichangjun/Documents/GitHub/insta-wizbee/premium_v3_test.jpg"
    )
    print("✨ Premium V3 Card Created: premium_v3_test.jpg")
