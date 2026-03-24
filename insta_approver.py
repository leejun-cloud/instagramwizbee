import json
import os
import requests
from datetime import datetime

# Configuration
DATA_FILE = "book_data.json"
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def get_next_unapproved_posts(limit=7):
    """주 데이터 파일에서 승인되지 않은 다음 n개의 포스트를 가져옵니다."""
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found.")
        return []

    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 아직 승인되지 않은 포스트 필터링
        unapproved = [post for post in data if not post.get("approved", False)]
        return unapproved[:limit]
    except Exception as e:
        print(f"Error reading {DATA_FILE}: {e}")
        return []

def send_to_slack(posts):
    """슬랙 웹훅을 통해 포스트 목록을 전송합니다."""
    if not SLACK_WEBHOOK_URL:
        print("Error: SLACK_WEBHOOK_URL environment variable is not set.")
        return

    if not posts:
        message = "✅ 모든 포스트가 승인되었습니다. 이번 주에 새로 승인할 포스트가 없습니다."
    else:
        message = "📢 *[위즈비] 이번 주 인스타그램 업로드 예정 리스트 (승인 대기)*\n\n"
        for post in posts:
            message += f"*Day {post['day']}: {post['book_title']}*\n"
            message += f"> *Hook:* {post['hook']}\n"
            message += f"> *Time:* {post['scheduled_time']}\n"
            message += f"> *Prompt:* `{post['image_prompt']}`\n\n"
        
        message += "\n압승인하시려면 `book_data.json`에서 해당 Day의 `approved`를 `true`로 변경해주세요."

    payload = {"text": message}
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        if response.status_code == 200:
            print("Successfully sent message to Slack.")
        else:
            print(f"Failed to send to Slack: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error sending request to Slack: {e}")

if __name__ == "__main__":
    next_posts = get_next_unapproved_posts()
    send_to_slack(next_posts)
