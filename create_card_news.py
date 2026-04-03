import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_gradient(width, height, color1, color2):
    """Creates a vertical gradient image."""
    base = Image.new('RGB', (width, height), color1)
    top = Image.new('RGB', (width, height), color2)
    mask = Image.new('L', (width, height))
    for y in range(height):
        for x in range(width):
            mask.putpixel((x, y), int(255 * (y / height)))
    base.paste(top, (0, 0), mask)
    return base

def draw_text_centered(draw, text, font, color, width, height, line_spacing=1.5):
    """Draws multi-line text centered on the image."""
    lines = []
    # Simple word wrapping for Korean (characters)
    words = text.split()
    current_line = ""
    max_line_width = width * 0.8
    
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_line_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
        
    line_heights = [draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in lines]
    total_text_height = sum(line_heights) + (len(lines) - 1) * (font.size * (line_spacing - 1))
    
    y = (height - total_text_height) / 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        x = (width - (bbox[2] - bbox[0])) / 2
        draw.text((x, y), line, font=font, fill=color)
        y += font.size * line_spacing

def generate_card(quote, output_path, title="Wizbee", style_params=None):
    width, height = 1080, 1080
    
    # Defaults (Premium Gold Theme)
    bg_color_top = (18, 18, 18)
    bg_color_bottom = (40, 40, 45)
    text_color = (255, 230, 180)
    
    # Overwrite with style_params if provided
    if style_params:
        bg_color_top = style_params.get('bg_top', bg_color_top)
        bg_color_bottom = style_params.get('bg_bottom', bg_color_bottom)
        text_color = style_params.get('text_color', text_color)
    
    img = create_gradient(width, height, bg_color_top, bg_color_bottom)
    draw = ImageDraw.Draw(img)
    
    # Try to find a good font
    font_paths = [
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf", # Mac
        "/Library/Fonts/AppleGothic.ttf", # Mac
        "/System/Library/Fonts/AppleSDGothicNeo.ttc", # Mac
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", # Linux
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", # Linux
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf", # Linux (Nanum)
        "Arial.ttf", # Generic
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" # Linux fallback
    ]
    
    font = None
    for path in font_paths:
        if os.path.exists(path):
            try:
                font = ImageFont.truetype(path, 60)
                print(f"Using font: {path}")
                break
            except:
                continue
    
    if not font:
        font = ImageFont.load_default()
        print("Warning: Using default font. Might not support Korean.")
        
    draw_text_centered(draw, quote, font, text_color, width, height)
    
    # Add Title/Logo
    try:
        small_font = ImageFont.truetype(font.path if hasattr(font, 'path') else "/Library/Fonts/AppleGothic.ttf", 40)
        draw.text((width/2 - 50, height - 100), title, font=small_font, fill=(150, 150, 150))
    except:
        pass
        
    # Add a subtle border or accent
    draw.rectangle([40, 40, width-40, height-40], outline=(100, 100, 110), width=2)
    
    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, quality=95)
    print(f"Generated: {output_path}")

quotes = [
    "직원들이 내부 위험을 견뎌야 하는 조직은 외부 위험에 대처하기 어려워진다.",
    "목표실적을 달성하기위해 직원들을 희생시켜도 괜찮다고 생각하는 리더들은 그렇게 했을때 일련의 결과가 어떻게 나타날지까지 고려해야 한다. 해결방법은 단 하나다. 바로 직장 내 안전망을 형성하고 유지하는 것이다",
    "진정한 리더는 마지막에 먹는다",
    "신뢰란 기계에 칠하는 윤활유와 같다. 신뢰는 마찰을 줄이고 더 높은 성과를 내기에 적합한 환경을 만든다.",
    "사람들에게 시간과 에너지를 쏟으라. 신뢰를 형성하는데 시간이 걸리며 그 속도를 빠르게 해주는 앱 같은 건 없다",
    "가까워지는 것이 먼저다. 적들은 싸우지만 친구들은 협력한다",
    "인간이 5만년 동안 번영한 이유는 자시 자신이 아니라 다른 사람을 섬겼기 때문이다"
]

if __name__ == "__main__":
    for i, quote in enumerate(quotes):
        generate_card(quote, f"/tmp/card_{i+1}.png")
