import os
import json
import requests
import re
import subprocess
from dotenv import load_dotenv

load_dotenv()

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")
DATA_FILE = "book_data.json"
LOG_FILE = "error.log"

def send_report(message, color="#e74c3c"):
    if not SLACK_WEBHOOK: return
    payload = {
        "attachments": [{
            "fallback": "Self-Healing Report",
            "color": color,
            "title": "🛡️ Wizbee Self-Healing AI Report",
            "text": message
        }]
    }
    requests.post(SLACK_WEBHOOK, json=payload)

def fix_json():
    """Attempts to fix a corrupted book_data.json."""
    if not os.path.exists(DATA_FILE): return False
    
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            json.load(f)
        return True # It's actually fine
    except json.JSONDecodeError:
        print("🩹 JSON 깨짐 감지. 자동 복구를 시도합니다.")
        # Simple fix: Try to close open brackets/braces if the last line is cut off
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            
        if not content.endswith("]"):
            # Fix unclosed quotes
            if content.count('"') % 2 != 0:
                content += '"'
            
            if content.endswith("}"): content += "]"
            elif content.endswith(","): content = content[:-1] + "}]"
            else: content += "}]"
            
        try:
            json.loads(content)
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except:
            return False

def self_heal():
    reason = "알 수 없는 오류"
    fixed = False
    
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            error_text = f.read()
            
        if "JSONDecodeError" in error_text:
            reason = "JSON 데이터 파일 손상"
            fixed = fix_json()
        elif "368" in error_text:
            reason = "인스타그램 정책/한도 초과 (Action Blocked)"
            fixed = False # We can't fix this automatically, only wait
        elif "image_path" in error_text:
            reason = "이미지 생성 실패"
            fixed = True # We'll retry, create_card_news.py handles the rest
        elif "Permission denied" in error_text:
            reason = "환경 설정/권한 문제"
            fixed = False
            
    if fixed:
        msg = f"✅ **오류 자동 교정 성공**\n\n*   **원인:** {reason}\n*   **조치:** 데이터 파일 복구 및 재생성 준비 완료\n*   **상태:** 자동 재시도를 시작합니다."
        send_report(msg, "#2ecc71")
        return True
    else:
        msg = f"❌ **오류 자동 교정 실패**\n\n*   **원인:** {reason}\n*   **조치:** 제가 고칠 수 없는 문제입니다. 직접 확인이 필요합니다.\n*   *시스템을 일시 중단합니다.*"
        send_report(msg, "#e74c3c")
        return False

if __name__ == "__main__":
    if self_heal():
        # Trigger GitHub workflow dispatch or local retry if possible
        print("Healed. Ready for retry.")
    else:
        print("Unhealable. Manual intervention required.")
