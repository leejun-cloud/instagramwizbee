import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

class InstaWizbeeV3:
    def __init__(self, project_root="/Users/ichangjun/Documents/GitHub/insta-wizbee"):
        self.project_root = project_root
        self.assets_dir = os.path.join(project_root, "assets")
        self.bg_dir = os.path.join(self.assets_dir, "backgrounds")
        self.font_dir = os.path.join(self.assets_dir, "fonts")
        
        # Default settings
        self.width = 1080
        self.height = 1080
        
    def get_random_bg(self):
        if not os.path.exists(self.bg_dir):
            return None
        bgs = [f for f in os.listdir(self.bg_dir) if f.endswith(('.png', '.jpg'))]
        if not bgs:
            return None
        return os.path.join(self.bg_dir, random.choice(bgs))

    def get_available_fonts(self):
        if not os.path.exists(self.font_dir):
            return []
        return [os.path.join(self.font_dir, f) for f in os.listdir(self.font_dir) if f.endswith(('.ttf', '.otf', '.TTF'))]

    def create_card(self, title, content, output_path, font_path=None, bg_path=None):
        # 1. Background Selection
        if not bg_path:
            bg_path = self.get_random_bg()
        
        if bg_path and os.path.exists(bg_path):
            img = Image.open(bg_path).convert("RGBA")
            img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
        else:
            # Gradient fallback
            img = Image.new("RGBA", (self.width, self.height), (240, 240, 240, 255))
            
        # 2. Premium Overlay (Vignette + Tint) for readability
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 50)) 
        img = Image.alpha_composite(img, overlay)
        
        draw = ImageDraw.Draw(img)
        
        # 3. Font Selection
        if not font_path:
            fonts = self.get_available_fonts()
            font_path = fonts[0] if fonts else None
            
        try:
            title_font = ImageFont.truetype(font_path, 85) if font_path else ImageFont.load_default()
            content_font = ImageFont.truetype(font_path, 50) if font_path else ImageFont.load_default()
        except:
            title_font = ImageFont.load_default()
            content_font = ImageFont.load_default()

        # 4. Draw Typography (Centered Layout)
        tw, th = self.get_text_size(draw, title, title_font)
        draw.text(((self.width - tw) / 2, self.height / 2 - 120), title, font=title_font, fill="white")
        
        lines = self.wrap_text(content, content_font, self.width - 240)
        y_text = self.height / 2 + 30
        for line in lines:
            lw, lh = self.get_text_size(draw, line, content_font)
            draw.text(((self.width - lw) / 2, y_text), line, font=content_font, fill="white")
            y_text += lh + 15

        # 5. Save Final Result
        final_img = img.convert("RGB")
        final_img.save(output_path, "JPEG", quality=95)
        return output_path

    def get_text_size(self, draw, text, font):
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    def wrap_text(self, text, font, max_width):
        lines = []
        words = text.split(' ')
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            # Using getlength is more robust in modern Pillow
            try:
                w = font.getlength(test_line)
            except:
                # Fallback for older Pillow
                w = font.getsize(test_line)[0]
                
            if w <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

if __name__ == "__main__":
    v3 = InstaWizbeeV3()
    # Sample Test
    v3.create_card(
        "당신을 위한 한마디", 
        "가장 어두운 밤이 지나야 가장 밝은 해가 뜹니다.\n오늘 하루도 정말 고생 많으셨어요.", 
        "/Users/ichangjun/Documents/GitHub/insta-wizbee/sample_v3_demo.jpg"
    )
    print("✨ Premium Card Created: sample_v3_demo.jpg")
