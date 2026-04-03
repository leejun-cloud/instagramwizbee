"""
card_maker_v2.py

28가지 다양한 스타일을 지원하는 카드뉴스 생성기.
최근 추가된 8종의 레퍼런스를 포함하여 총 28종의 스타일 팔레트와 데코레이션을 지원합니다.
"""

import os
import random
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ─────────────────────────────────────────────
# 폰트 경로 목록
# ─────────────────────────────────────────────
FONT_PATHS = [
    "/System/Library/Fonts/Supplemental/AppleMyungjo.ttf",
    "/Library/Fonts/NanumBrush.ttf",
    "/Library/Fonts/NanumPen.ttf",
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
]

BRAND_NAME = "품성독서"
WIDTH, HEIGHT = 1080, 1080

# ─────────────────────────────────────────────
# 스타일 팔레트 28종
# ─────────────────────────────────────────────
STYLE_PALETTES = [
    # 1-10: 기본 및 감성 스타일
    {"name": "classic_white", "bg": (252, 250, 245), "text_main": (20, 20, 20), "text_sub": (80, 80, 80), "accent": (200, 60, 60), "brand": (150, 100, 80), "deco": "plant"},
    {"name": "cream_floral", "bg": (255, 252, 235), "text_main": (40, 30, 20), "text_sub": (100, 80, 60), "accent": (220, 100, 100), "brand": (160, 120, 80), "deco": "flower"},
    {"name": "sky_minimal", "bg": (240, 248, 255), "text_main": (20, 40, 80), "text_sub": (70, 100, 140), "accent": (80, 160, 220), "brand": (80, 120, 180), "deco": "branch"},
    {"name": "nature_green", "bg": (245, 252, 240), "text_main": (30, 50, 30), "text_sub": (80, 110, 70), "accent": (60, 160, 80), "brand": (80, 120, 60), "deco": "plant"},
    {"name": "soft_pink", "bg": (255, 245, 248), "text_main": (60, 20, 40), "text_sub": (120, 70, 90), "accent": (220, 80, 120), "brand": (180, 90, 110), "deco": "heart"},
    {"name": "dark_bloom", "bg": (25, 25, 28), "text_main": (250, 250, 250), "text_sub": (180, 180, 190), "accent": (200, 100, 150), "brand": (150, 150, 160), "deco": "dark_flower"},
    {"name": "yellow_field", "bg": (90, 180, 220), "text_main": (255, 255, 255), "text_sub": (220, 230, 240), "accent": (255, 230, 90), "brand": (240, 240, 250), "deco": "field"},
    {"name": "sunset_warm", "bg": (210, 120, 70), "text_main": (30, 20, 10), "text_sub": (60, 40, 20), "accent": (255, 210, 110), "brand": (50, 30, 20), "deco": "sun"},
    {"name": "autumn_leaves", "bg": (235, 225, 210), "text_main": (60, 40, 30), "text_sub": (110, 80, 60), "accent": (190, 100, 50), "brand": (130, 90, 70), "deco": "leaf"},
    {"name": "vintage_paper", "bg": (210, 190, 160), "text_main": (70, 50, 40), "text_sub": (110, 90, 80), "accent": (150, 70, 50), "brand": (100, 80, 60), "deco": "branch"},

    # 11-20: 레퍼런스 기반 1차 추가 스타일
    {"name": "heart_hands", "bg": (240, 245, 245), "text_main": (40, 50, 60), "text_sub": (100, 110, 120), "accent": (220, 60, 60), "brand": (100, 110, 120), "deco": "heart_hands"},
    {"name": "camera_blossom", "bg": (255, 245, 240), "text_main": (30, 30, 30), "text_sub": (80, 80, 80), "accent": (230, 130, 150), "brand": (150, 100, 120), "deco": "camera"},
    {"name": "wooden_cross", "bg": (30, 40, 35), "text_main": (240, 240, 230), "text_sub": (180, 180, 170), "accent": (200, 180, 150), "brand": (150, 140, 120), "deco": "cross"},
    {"name": "roses_table", "bg": (245, 245, 240), "text_main": (20, 20, 20), "text_sub": (80, 80, 80), "accent": (200, 30, 40), "brand": (120, 50, 50), "deco": "rose"},
    {"name": "yellow_flower_blur", "bg": (160, 190, 120), "text_main": (30, 50, 30), "text_sub": (80, 100, 80), "accent": (250, 220, 50), "brand": (60, 90, 60), "deco": "yellow_flower"},
    {"name": "watercolor_path", "bg": (250, 250, 250), "text_main": (30, 30, 30), "text_sub": (80, 80, 80), "accent": (200, 120, 40), "brand": (100, 80, 60), "deco": "wc_tree"},
    {"name": "minimal_wall", "bg": (235, 235, 240), "text_main": (40, 40, 45), "text_sub": (100, 100, 110), "accent": (60, 60, 70), "brand": (120, 120, 130), "deco": "none"},
    {"name": "notebook_pen", "bg": (240, 235, 225), "text_main": (50, 40, 30), "text_sub": (100, 90, 80), "accent": (100, 120, 140), "brand": (80, 70, 60), "deco": "pen"},
    {"name": "daisy_border", "bg": (245, 245, 240), "text_main": (30, 30, 30), "text_sub": (90, 90, 90), "accent": (240, 200, 50), "brand": (100, 100, 100), "deco": "daisy"},
    {"name": "falling_leaves_blur", "bg": (210, 180, 150), "text_main": (40, 30, 20), "text_sub": (90, 70, 50), "accent": (180, 80, 40), "brand": (120, 90, 60), "deco": "leaf"},

    # 21-28: 레퍼런스 기반 2차 추가 스타일
    {"name": "lime_slice", "bg": (245, 245, 245), "text_main": (30, 30, 30), "text_sub": (90, 90, 90), "accent": (100, 180, 60), "brand": (120, 120, 120), "deco": "lime"},
    {"name": "sky_bird", "bg": (170, 210, 240), "text_main": (20, 30, 50), "text_sub": (60, 80, 100), "accent": (255, 255, 255), "brand": (50, 70, 90), "deco": "bird"},
    {"name": "hands_card", "bg": (60, 50, 40), "text_main": (20, 20, 20), "text_sub": (60, 60, 60), "accent": (180, 40, 80), "brand": (100, 80, 60), "deco": "hands_card"},
    {"name": "jar_hearts", "bg": (252, 248, 235), "text_main": (50, 40, 30), "text_sub": (100, 90, 80), "accent": (230, 80, 100), "brand": (120, 100, 80), "deco": "jar"},
    {"name": "lavender_side", "bg": (250, 250, 255), "text_main": (40, 40, 60), "text_sub": (100, 100, 130), "accent": (150, 100, 220), "brand": (120, 120, 150), "deco": "lavender"},
    {"name": "envelope_ribbon", "bg": (220, 230, 220), "text_main": (30, 40, 30), "text_sub": (80, 90, 80), "accent": (240, 140, 160), "brand": (100, 110, 100), "deco": "envelope"},
    {"name": "walking_man", "bg": (240, 240, 240), "text_main": (50, 50, 55), "text_sub": (110, 110, 120), "accent": (80, 90, 130), "brand": (100, 100, 110), "deco": "man"},
    {"name": "single_daisy_focus", "bg": (220, 230, 180), "text_main": (40, 50, 30), "text_sub": (90, 100, 80), "accent": (255, 255, 255), "brand": (70, 80, 60), "deco": "single_daisy"},
]

def load_font(size):
    for path in FONT_PATHS:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()

def draw_decoration(draw, style, width, height):
    deco = style["deco"]
    accent = style["accent"]
    sub = style["text_sub"]
    
    if deco == "plant":
        _draw_plant(draw, width - 200, height - 250, accent)
    elif deco == "flower" or deco == "dark_flower":
        _draw_flower_corner(draw, width, height, accent, dark=(deco == "dark_flower"))
    elif deco == "branch":
        _draw_branch(draw, width // 2, 80, accent)
    elif deco == "heart":
        _draw_heart(draw, width // 2, 120, accent)
    elif deco == "field":
        _draw_field(draw, width, height, accent)
    elif deco == "sun":
        _draw_sun(draw, width // 2, 180, accent)
    elif deco == "leaf":
        _draw_leaf(draw, width - 150, height - 200, accent)
    elif deco == "heart_hands":
        _draw_heart(draw, width // 2, height - 150, accent)
        draw.polygon([(width//2-40, height), (width//2-80, height-100), (width//2-20, height-120), (width//2, height)], fill=(240, 180, 180))
        draw.polygon([(width//2+40, height), (width//2+80, height-100), (width//2+20, height-120), (width//2, height)], fill=(240, 180, 180))
    elif deco == "camera":
        _draw_camera(draw, width // 2, height - 180, sub)
        _draw_flower_corner(draw, width//2 + 50, height - 250, accent, dark=False, scale=0.6)
    elif deco == "cross":
        _draw_cross(draw, 200, height // 2, (180, 170, 150))
    elif deco == "rose":
        _draw_rose(draw, width // 2, 150, accent)
    elif deco == "yellow_flower":
        _draw_flower_corner(draw, 150, height - 150, accent, scale=1.2)
    elif deco == "wc_tree":
        _draw_wc_tree(draw, width - 200, height - 300, accent)
    elif deco == "pen":
        _draw_pen(draw, width // 2, height - 150, sub)
    elif deco == "daisy":
        _draw_daisy(draw, 100, 100)
        _draw_daisy(draw, width - 150, height - 150)
    elif deco == "lime":
        _draw_lime_slice(draw, width // 2, height - 50, 450)
    elif deco == "bird":
        _draw_bird(draw, width // 2, height - 200, (100, 80, 60))
    elif deco == "hands_card":
        _draw_hands_holding_card(draw, width, height)
    elif deco == "jar":
        _draw_jar(draw, width // 2, height - 100, accent)
    elif deco == "lavender":
        _draw_lavender(draw, 100, height // 2, accent)
        _draw_lavender(draw, width - 100, height // 2, accent)
    elif deco == "envelope":
        _draw_envelope(draw, width // 2, height - 200, sub, accent)
    elif deco == "man":
        _draw_man_walking(draw, 300, height - 200)
    elif deco == "single_daisy":
        _draw_daisy(draw, width // 2 - 200, height // 2 + 100, scale=3.0)

# --- 데코 그리기 헬퍼 ---
def _draw_lime_slice(draw, cx, cy, radius):
    box = [cx - radius, cy - radius, cx + radius, cy + radius]
    draw.pieslice(box, 180, 360, fill=(150, 220, 80), outline=(220, 255, 180), width=15)
    for ang in range(200, 350, 30):
        rad = math.radians(ang)
        draw.line([(cx, cy), (cx + math.cos(rad) * radius, cy + math.sin(rad) * radius)], fill=(220, 255, 180), width=8)

def _draw_bird(draw, cx, cy, color):
    draw.line([(cx - 150, cy + 100), (cx + 150, cy + 100)], fill=color, width=5)
    draw.ellipse([cx - 30, cy + 40, cx + 50, cy + 90], fill=(200, 200, 200))
    draw.ellipse([cx - 50, cy + 20, cx, cy + 60], fill=(200, 200, 200))

def _draw_hands_holding_card(draw, width, height):
    # 배경에 카드 그리기
    card_margin = 150
    draw.rectangle([card_margin, card_margin, width - card_margin, height - card_margin], fill=(252, 250, 245))
    hand_color = (250, 220, 180)
    draw.ellipse([50, 50, 250, 250], fill=hand_color) 
    draw.ellipse([width - 250, 50, width - 50, 250], fill=hand_color)

def _draw_jar(draw, cx, cy, accent):
    draw.rectangle([cx - 100, cy - 150, cx + 100, cy + 50], outline=(180, 180, 180), width=3)
    for i in range(5):
        _draw_heart(draw, cx + random.randint(-60, 60), cy + random.randint(-100, 20), accent)

def _draw_lavender(draw, x, y, color):
    draw.line([(x, y + 200), (x, y - 200)], fill=(100, 150, 100), width=4)
    for i in range(-5, 6):
        draw.ellipse([x-15, y+i*40-10, x+15, y+i*40+10], fill=color)

def _draw_envelope(draw, cx, cy, color, accent):
    draw.rectangle([cx - 200, cy - 120, cx + 200, cy + 120], fill=color)
    _draw_heart(draw, cx, cy, accent)

def _draw_man_walking(draw, x, y):
    draw.ellipse([x - 20, y - 100, x + 20, y - 60], fill=(80, 80, 80))
    draw.rectangle([x - 30, y - 60, x + 30, y + 20], fill=(100, 110, 130))

def _draw_plant(draw, x, y, leaf_color):
    draw.polygon([(x, y+70), (x+100, y+70), (x+90, y+130), (x+10, y+130)], fill=(200, 150, 100))
    draw.line([(x+50, y+65), (x+50, y)], fill=(100, 140, 80), width=5)
    draw.ellipse([x-5, y-10, x+35, y+15], fill=leaf_color)
    draw.ellipse([x+65, y-15, x+105, y+5], fill=leaf_color)

def _draw_flower_corner(draw, cx, cy, accent, dark=False, scale=1.0):
    for dx, dy in [(0, -28), (28, 0), (0, 28), (-28, 0)]:
        d_x, d_y = int(dx * scale), int(dy * scale)
        r = int(16 * scale)
        draw.ellipse([cx + d_x - r, cy + d_y - r, cx + d_x + r, cy + d_y + r], fill=accent)

def _draw_branch(draw, cx, cy, accent):
    draw.line([(cx, cy-40), (cx, cy+20)], fill=(160, 130, 90), width=3)
    draw.ellipse([cx - 20, cy-10, cx + 20, cy+10], fill=accent)

def _draw_heart(draw, cx, cy, color):
    r = 30
    draw.ellipse([cx - r, cy - r // 2, cx, cy + r // 2], fill=color)
    draw.ellipse([cx, cy - r // 2, cx + r, cy + r // 2], fill=color)
    draw.polygon([(cx - r, cy + r // 6), (cx + r, cy + r // 6), (cx, cy + r + 10)], fill=color)

def _draw_field(draw, width, height, color):
    for i in range(50):
        x = random.randint(0, width - 10)
        y = random.randint(height - 100, height - 10)
        draw.ellipse([x, y, x+10, y+10], fill=color)

def _draw_sun(draw, cx, cy, color):
    draw.ellipse([cx - 60, cy - 60, cx + 60, cy + 60], fill=color)

def _draw_leaf(draw, x, y, color):
    draw.ellipse([x, y, x+60, y+30], fill=color)

def _draw_camera(draw, cx, cy, color):
    draw.rectangle([cx - 60, cy - 40, cx + 60, cy + 40], outline=color, width=3)

def _draw_cross(draw, cx, cy, color):
    draw.rectangle([cx - 15, cy - 60, cx + 15, cy + 60], fill=color)
    draw.rectangle([cx - 45, cy - 10, cx + 45, cy + 10], fill=color)

def _draw_rose(draw, cx, cy, color):
    draw.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=color)

def _draw_wc_tree(draw, cx, cy, color):
    draw.line([(cx, cy + 80), (cx, cy)], fill=(60, 40, 20), width=5)
    for i in range(15):
        rx, ry = cx + random.randint(-40, 40), cy + random.randint(-40, 40)
        r = 15
        draw.ellipse([rx - r, ry - r, rx + r, ry + r], fill=color)

def _draw_pen(draw, cx, cy, color):
    draw.rectangle([cx - 5, cy, cx + 5, cy + 80], fill=color)

def _draw_daisy(draw, cx, cy, scale=1.0):
    for dx, dy in [(0, -20), (20, 0), (0, 20), (-20, 0)]:
        r = int(10 * scale)
        d_x, d_y = int(dx * scale), int(dy * scale)
        draw.ellipse([cx + d_x - r, cy + d_y - r, cx + d_x + r, cy + d_y + r], fill=(255, 255, 255))
    r_core = int(8 * scale)
    draw.ellipse([cx - r_core, cy - r_core, cx + r_core, cy + r_core], fill=(255, 200, 0))

# --- 텍스트 배지 헬퍼 ---
def split_quote_smart(quote: str):
    words = quote.split()
    if not words: return []
    chunks = [{"text": words[0], "big": True}]
    rest = words[1:]
    for i in range(0, len(rest), 3):
        chunks.append({"text": " ".join(rest[i:i + 3]), "big": False})
    return chunks

def draw_quote_blocks(draw, quote, style, width, height):
    chunks = split_quote_smart(quote)
    big_size, normal_size = 80, 52
    font_big, font_normal = load_font(big_size), load_font(normal_size)
    max_w = int(width * 0.8)
    
    lines = []
    for chunk in chunks:
        font = font_big if chunk["big"] else font_normal
        cur_line = ""
        for word in chunk["text"].split():
            test = (cur_line + " " + word).strip()
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] > max_w and cur_line:
                lines.append({"text": cur_line, "font": font, "big": chunk["big"]})
                cur_line = word
            else:
                cur_line = test
        if cur_line:
            lines.append({"text": cur_line, "font": font, "big": chunk["big"]})

    y = height * 0.3
    if style["deco"] == "hands_card": y = height * 0.28

    for line in lines:
        bbox = draw.textbbox((0, 0), line["text"], font=line["font"])
        lh = bbox[3] - bbox[1]
        x = (width - (bbox[2] - bbox[0])) / 2
        color = style["accent"] if line["big"] else style["text_main"]
        draw.text((x, y), line["text"], font=line["font"], fill=color)
        y += lh + 25

def draw_branding(draw, style, width, height):
    font = load_font(26)
    bbox = draw.textbbox((0, 0), BRAND_NAME, font=font)
    draw.text((width - (bbox[2] - bbox[0]) - 60, height - 80), BRAND_NAME, font=font, fill=style["brand"])

def generate_card_v2(quote: str, output_path: str, style_index: int = 0):
    style = STYLE_PALETTES[style_index % len(STYLE_PALETTES)]
    img = Image.new("RGB", (WIDTH, HEIGHT), style["bg"])
    draw = ImageDraw.Draw(img)
    draw_decoration(draw, style, WIDTH, HEIGHT)
    draw_quote_blocks(draw, quote, style, WIDTH, HEIGHT)
    draw_branding(draw, style, WIDTH, HEIGHT)
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    img.save(output_path, quality=98)
    return output_path

if __name__ == "__main__":
    sample_quote = "진정한 삶은\n어제와 다른 오늘을\n살아내는 것이다."
    for i in range(len(STYLE_PALETTES)):
        generate_card_v2(sample_quote, f"images/style_sample_{i+1:02d}.png", style_index=i)
    print(f"✅ 총 {len(STYLE_PALETTES)}종의 스타일 샘플 생성이 완료되었습니다 (images/ 폴더 확인)")
