import requests
import time
import json
import os
import sys

import os
from dotenv import load_dotenv

load_dotenv() # Load local .env if exists

# Configuration
ACCOUNT_ID = os.getenv("INSTA_ACCOUNT_ID", "17841427998042847")
ACCESS_TOKEN = os.getenv("INSTA_ACCESS_TOKEN", "IGAALM9q47OQ1BZAFkzY0hzZAW0ybTRfYXhYZAkNxQXgwSlRwUnpOMGJrdnFudHJNcWpqQ2J3dFpuYW9BSnVGYmhONjJrcDBkamxzakFCWVdBeFBiMDRRSHdjaElpZADh0WVB1M1lZANEdZASHc4eWZAON2pjSE5uQXNzX2xvV1VETlZAQRQZDZD")
DATA_FILE = "book_data.json"
VERSION = "v23.0"

def get_public_url(file_path):
    """Hosts local file to a public URL using Catbox."""
    try:
        with open(file_path, 'rb') as f:
            response = requests.post('https://catbox.moe/user/api.php', 
                                   data={'reqtype': 'fileupload'}, 
                                   files={'fileToUpload': f})
        if response.status_code == 200:
            return response.text.strip()
    except Exception as e:
        print(f"Error hosting file: {e}")
    return None

def publish_to_insta(image_url, caption):
    """Handles the 2-step Instagram API process."""
    base_url = f"https://graph.instagram.com/{VERSION}/{ACCOUNT_ID}"
    
    # 1. Container
    res = requests.post(f"{base_url}/media", data={
        "image_url": image_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }).json()
    creation_id = res.get("id")
    if not creation_id:
        return f"Error: {res}"
    
    # Processing wait
    print(f"⏳ 인스타그램 서버에서 미디어를 처리 중입니다... (Creation ID: {creation_id})")
    time.sleep(60) 
    
    # 2. Publish
    publish_res = requests.post(f"{base_url}/media_publish", data={
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN
    }).json()
    return publish_res.get("id")

def run_day(day_num, image_path=None, test_mode=False):
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    day_info = next((d for d in data if d["day"] == day_num), None)
    if not day_info:
        print(f"Day {day_num} 정보를 찾을 수 없습니다.")
        return

    # 승인 여부 확인
    is_approved = day_info.get("approved", False)
    if not is_approved and not test_mode:
        print(f"❌ Day {day_num} 포스트는 아직 승인되지 않았습니다. 업로드를 취소합니다.")
        return

    # 캡션 구성: Hook -> 발췌문 -> 책 제목 -> 본문 캡션 -> 해시태그
    full_caption = (
        f"{day_info['hook']}\n\n"
        f"📖 \"{day_info['excerpt']}\"\n"
        f"─ {day_info['book_title']}\n\n"
        f"{day_info['caption']}\n\n"
        f"{day_info['hashtags']}\n\n"
        f"#위즈비 #Wizbee #북스타그램 #독서명언"
    )
    
    if test_mode:
        print("--- [TEST MODE] ---")
        print(f"Day {day_num} 예정 시간: {day_info.get('scheduled_time', 'N/A')}")
        print(f"생성할 이미지 프롬프트: {day_info['image_prompt']}")
        print(f"인스타그램 캡션 미리보기:\n{full_caption}")
        print("-------------------")
        return

    if not image_path:
        print("에러: 업로드할 이미지 경로가 필요합니다.")
        return

    public_url = get_public_url(image_path)
    if not public_url:
        print("에러: 이미지를 호스팅하는 데 실패했습니다.")
        return

    print(f"Day {day_num}: 인스타그램 업로드 시작...")
    res = publish_to_insta(public_url, full_caption)
    print(f"업로드 결과 ID: {res}")

def run_auto(test_mode=False):
    """Automatically finds the next approved post to publish."""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 아직 발행되지 않았고 승인된 포스트 찾기
    # 'published' 필드가 없거나 False인 것 중 가장 작은 day
    pending_posts = [p for p in data if p.get("approved", False) and not p.get("published", False)]
    
    if not pending_posts:
        print("💡 발행 대기 중인 승인된 포스트가 없습니다.")
        return

    # 첫 번째 대기 포스트 선택
    post = pending_posts[0]
    day_num = post["day"]
    
    print(f"📌 [Auto] Day {day_num} 포스트 발행을 시도합니다.")
    
    # 이미지 경로 확인 (로컬에 해당 day 전용 이미지가 있는지 확인하는 로직 추가 가능)
    # 현재는 수동 업로드 방식이므로, 이미지 경로가 지정되지 않으면 중단
    # (나중에 AI 이미지 생성 연동 시 여기를 확장)
    image_path = f"images/day_{day_num}.png"
    if not os.path.exists(image_path):
        # 만약 images 폴더에 없다면 test_image.png라도 있는지 확인 (임시)
        if os.path.exists("test_image.png"):
            image_path = "test_image.png"
            print(f"⚠️ Day {day_num} 전용 이미지가 없어 test_image.png를 사용합니다.")
        else:
            print(f"❌ 에러: Day {day_num}에 해당하는 이미지({image_path})가 없습니다.")
            return

    run_day(day_num, image_path, test_mode=test_mode)
    
    # 발행 성공 시 (테스트 모드가 아닐 때) published 처리
    if not test_mode:
        for p in data:
            if p["day"] == day_num:
                p["published"] = True
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Day {day_num} 발행 완료 및 데이터 업데이트.")

if __name__ == "__main__":
    is_test = "--test" in sys.argv
    is_auto = "--auto" in sys.argv
    
    if is_auto:
        run_auto(test_mode=is_test)
    elif len(sys.argv) < 2:
        print("사용법: ")
        print("  수동: python insta_autopilot.py <day_number> [image_path] [--test]")
        print("  자동: python insta_autopilot.py --auto [--test]")
    else:
        try:
            day = int(sys.argv[1])
            img = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "--test" else None
            run_day(day, img, test_mode=is_test)
        except ValueError:
            print("에러: 올바른 day_number를 입력하거나 --auto 옵션을 사용하세요.")
