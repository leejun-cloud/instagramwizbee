import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration (Existing credentials)
ACCOUNT_ID = os.getenv("INSTA_ACCOUNT_ID", "17841427998042847")
ACCESS_TOKEN = os.getenv("INSTA_ACCESS_TOKEN", "REDACTED_INSTA_TOKEN")
VERSION = "v23.0"

class InstaCommenter:
    def __init__(self):
        self.base_url = f"https://graph.instagram.com/{VERSION}"
        self.acc_id = ACCOUNT_ID
        self.token = ACCESS_TOKEN

    def get_recent_media(self, limit=5):
        """Fetches recent media IDs."""
        url = f"{self.base_url}/{self.acc_id}/media"
        params = {"access_token": self.token, "limit": limit}
        res = requests.get(url, params=params).json()
        return res.get("data", [])

    def get_comments(self, media_id):
        """Fetches comments for a specific media ID."""
        url = f"{self.base_url}/{media_id}/comments"
        params = {"access_token": self.token, "fields": "id,text,from,timestamp"}
        res = requests.get(url, params=params).json()
        return res.get("data", [])

    def get_replies(self, comment_id):
        """Fetches replies for a specific comment ID."""
        url = f"{self.base_url}/{comment_id}/replies"
        params = {"access_token": self.token, "fields": "id,text,from,timestamp"}
        res = requests.get(url, params=params).json()
        return res.get("data", [])

    def reply_to_comment(self, comment_id, message):
        """Posts a reply to a specific comment ID."""
        url = f"{self.base_url}/{comment_id}/replies"
        data = {"message": message, "access_token": self.token}
        res = requests.post(url, data=data).json()
        return res

    def generate_reply(self, comment_text, username):
        """Generates a contextual reply based on keywords."""
        text = comment_text.lower()
        
        # Simple keyword matching
        if any(kw in text for kw in ["감사", "고맙", "땡큐", "thanks"]):
            return f"@{username} 별말씀을요! 대장님께 도움이 되었다니 정말 기쁩니다. ✨"
        elif any(kw in text for kw in ["좋아", "굿", "good", "최고", "짱"]):
            return f"@{username} 긍정적인 에너지 감사합니다! 오늘도 대장님만의 멋진 하루 보내세요! 🚀"
        elif any(kw in text for kw in ["질문", "궁금", "어떻게", "how"]):
            return f"@{username} 대장님, 궁금하신 점은 언제든 말씀해 주세요! 제가 확인 후 답변 드리겠습니다. 🧐"
        
        # Default friendly reply
        return f"@{username} 대장님, 소중한 댓글 감사합니다! 좋은 하루 보내세요! 🌷"

    def run_auto_reply(self, dry_run=True):
        print(f"🔍 댓글 모니터링 시작 (Dry Run: {dry_run})...")
        media_list = self.get_recent_media()
        
        if not media_list:
            print("📭 최근 게시물이 없습니다.")
            return

        for media in media_list:
            media_id = media["id"]
            print(f"\n--- Post ID: {media_id} ---")
            comments = self.get_comments(media_id)
            
            if not comments:
                print("   - 아직 댓글이 없습니다.")
                continue

            for comment in comments:
                comment_id = comment["id"]
                comment_text = comment["text"]
                # In some cases 'from' might be missing, handle it
                comment_from = comment.get("from", {}).get("username", "대장님")
                
                print(f"💬 [{comment_from}]: {comment_text}")
                
                # Check if we already replied
                # To be thorough, we check if ANY reply from the account exists
                replies = self.get_replies(comment_id)
                already_replied = any(r.get("from", {}).get("username") == "verifiedinvestingh" for r in replies)
                
                if already_replied:
                    print("   ✅ 이미 답글을 달았습니다.")
                    continue
                
                # Logic to generate a reply
                reply_message = self.generate_reply(comment_text, comment_from)
                
                if dry_run:
                    print(f"   🚀 [DRY RUN] 보낼 답글: {reply_message}")
                else:
                    print(f"   🚀 답글 게시 중...")
                    res = self.reply_to_comment(comment_id, reply_message)
                    print(f"   결과: {res}")
                
                time.sleep(1) # Rate limit protection

if __name__ == "__main__":
    commenter = InstaCommenter()
    # First, run as dry run to see existing comments
    commenter.run_auto_reply(dry_run=True)
