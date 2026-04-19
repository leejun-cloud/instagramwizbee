import requests
import time
import json
import os
import sys
import traceback
import datetime
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db

load_dotenv()

# Configuration
ACCOUNT_ID = os.getenv("INSTA_ACCOUNT_ID")
ACCESS_TOKEN = os.getenv("INSTA_ACCESS_TOKEN")
VERSION = "v23.0"
DATABASE_URL = "https://insta-wizbee-cloud-2026-default-rtdb.firebaseio.com"
SLACK_ALERT_WEBHOOK_URL = os.getenv("SLACK_ALERT_WEBHOOK_URL") or os.getenv("SLACK_WEBHOOK_URL")


def notify_slack(message, level="info"):
    """Send a best-effort Slack notification. Silently no-ops if webhook is not set."""
    if not SLACK_ALERT_WEBHOOK_URL:
        return
    emoji = {"info": "ℹ️", "success": "✅", "warn": "⚠️", "error": "🚨"}.get(level, "🔔")
    try:
        requests.post(
            SLACK_ALERT_WEBHOOK_URL,
            json={"text": f"{emoji} *[insta-wizbee]* {message}"},
            timeout=10,
        )
    except Exception as e:
        # Never let alerting failure break the main flow
        print(f"⚠️ Slack alert failed: {e}")

# Firebase Setup (Realtime Database)
def init_fb():
    if not firebase_admin._apps:
        cred_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")
        if cred_json:
            # Check if it's a path or literal JSON
            if os.path.exists(cred_json):
                cred = credentials.Certificate(cred_json)
            else:
                import json
                cred_dict = json.loads(cred_json)
                cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred, {'databaseURL': DATABASE_URL})
        else:
            # Fallback to default or just DB URL (public access if configured)
            firebase_admin.initialize_app(options={'databaseURL': DATABASE_URL})
    return db.reference('posts')

def get_public_url(file_path):
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"⚠️ File not found for hosting: {file_path}")
            return None
            
        with open(file_path, 'rb') as f:
            response = requests.post('https://catbox.moe/user/api.php', 
                                   data={'reqtype': 'fileupload'}, 
                                   files={'fileToUpload': f},
                                   timeout=30)
        if response.status_code == 200:
            return response.text.strip()
        else:
            print(f"❌ Hosting failed (HTTP {response.status_code}): {response.text}")
    except Exception as e:
        print(f"❌ Error hosting file: {e}")
    return None

def wait_for_container_ready(creation_id, base_url, max_wait=180, interval=5):
    """Polls the media container's status_code until FINISHED (or hard fail).
    Replaces the old blind time.sleep(60) — large images used to fail because
    IG hadn't finished processing; tiny images wasted a minute."""
    url = f"https://graph.instagram.com/{VERSION}/{creation_id}"
    elapsed = 0
    while elapsed < max_wait:
        try:
            res = requests.get(
                url,
                params={"fields": "status_code,status", "access_token": ACCESS_TOKEN},
                timeout=15,
            ).json()
        except Exception as e:
            print(f"⚠️ Poll error (will retry): {e}")
            res = {}

        status = res.get("status_code")
        if status == "FINISHED":
            print(f"✅ Container ready after {elapsed}s")
            return True
        if status in ("ERROR", "EXPIRED"):
            print(f"❌ Container {status}: {res.get('status')}")
            return False

        print(f"… container {status or 'UNKNOWN'} ({elapsed}s elapsed)")
        time.sleep(interval)
        elapsed += interval

    print(f"⚠️ Timeout after {max_wait}s waiting for container")
    return False


def publish_to_insta(image_url, caption):
    if not ACCOUNT_ID or not ACCESS_TOKEN:
        return "Error: Missing INSTA_ACCOUNT_ID or INSTA_ACCESS_TOKEN"

    base_url = f"https://graph.instagram.com/{VERSION}/{ACCOUNT_ID}"
    try:
        res = requests.post(f"{base_url}/media", data={
            "image_url": image_url,
            "caption": caption,
            "access_token": ACCESS_TOKEN
        }, timeout=30).json()

        creation_id = res.get("id")
        if not creation_id:
            return f"Error: Container create failed - {res}"

        print(f"⏳ Waiting for Instagram to process (ID: {creation_id})...")
        if not wait_for_container_ready(creation_id, base_url):
            return f"Error: Container not ready (id={creation_id})"

        publish_res = requests.post(f"{base_url}/media_publish", data={
            "creation_id": creation_id,
            "access_token": ACCESS_TOKEN
        }, timeout=30).json()

        published_id = publish_res.get("id")
        if not published_id:
            return f"Error: Publish failed - {publish_res}"
        return published_id
    except Exception as e:
        return f"Error: {e}"

def run_auto(test_mode=False):
    posts_ref = init_fb()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    print(f"🔍 [RTDB-CLOUD] Checking for today ({today})...")
    
    # Get all posts from RTDB
    all_posts = posts_ref.get()
    if not all_posts:
        print("❌ No data in Realtime Database. Please use the [Seed] button first.")
        return

    # Find today's target (Flattened because RTDB might be a dict or list)
    posts_list = []
    if isinstance(all_posts, dict):
        posts_list = list(all_posts.values())
    elif isinstance(all_posts, list):
        posts_list = [p for p in all_posts if p is not None]

    # Schema note:
    #   scheduled_date : "YYYY-MM-DD"  (ISO date, optional — if set and matches today, priority)
    #   scheduled_time : "HH:MM"       (time-of-day string, optional — informational only)
    # If neither path matches today, we fall back to the oldest approved-unpublished post
    # so the feed keeps moving even when dates were never assigned.
    def _norm_date(v):
        if not v or not isinstance(v, str):
            return None
        v = v.strip()
        # Accept YYYY-MM-DD or YYYY/MM/DD; silently ignore anything else
        for sep in ("-", "/"):
            parts = v.split(sep)
            if len(parts) == 3 and all(p.isdigit() for p in parts):
                y, m, d = parts
                try:
                    return datetime.date(int(y), int(m), int(d)).isoformat()
                except ValueError:
                    return None
        return None

    target_post = None
    # 1. Match by scheduled_date == today
    target_post = next(
        (p for p in posts_list
         if _norm_date(p.get("scheduled_date")) == today
         and p.get("approved", False)
         and not p.get("published", False)),
        None,
    )

    # 2. Fallback to oldest approved-unpublished (by day number)
    if not target_post:
        pending = [p for p in posts_list if p.get("approved", False) and not p.get("published", False)]
        if pending:
            target_post = sorted(pending, key=lambda x: x.get("day", 9999))[0]
            print(f"ℹ️ No date-matched post for {today}; using oldest approved (Day {target_post.get('day')}).")

    if target_post:
        day_num = target_post["day"]
        print(f"🎯 Target Found: Day {day_num} ({target_post.get('hook', '')[:20]}...)")

        # --- Idempotency guard ---
        # Re-fetch this specific post right before publish. If cron fires twice, or
        # a manual workflow_dispatch races with the schedule, this check prevents
        # re-publishing the same content.
        fresh = posts_ref.child(str(day_num)).get() or {}
        if fresh.get("published"):
            print(f"🛑 Idempotency: Day {day_num} is already published. Abort.")
            return

        image_path = f"images/day_{day_num}.jpg"
        if not os.path.exists(image_path):
            image_path = f"images/day_{day_num}.png"

        if not os.path.exists(image_path):
            msg = f"Image missing (checked JPG/PNG): images/day_{day_num}. Skip."
            print(f"⚠️ {msg}")
            notify_slack(f"Day {day_num} 발행 스킵: {msg}", level="warn")
            return

        full_caption = f"{target_post['caption']}\n\n{target_post['hashtags']}"

        if test_mode:
            print(f"[TEST] Would publish Day {day_num}")
            return

        public_url = get_public_url(image_path)
        if not public_url:
            notify_slack(f"Day {day_num} 이미지 호스팅 실패 (catbox.moe)", level="error")
            return

        res = publish_to_insta(public_url, full_caption)
        print(f"Result: {res}")

        if res and not str(res).startswith("Error"):
            posts_ref.child(str(day_num)).update({"published": True})
            print(f"✅ RTDB Updated: Day {day_num} PUBLISHED.")
            notify_slack(
                f"Day {day_num} 발행 완료 — media_id=`{res}`\n> {target_post.get('hook', '')[:80]}",
                level="success",
            )
        else:
            notify_slack(f"Day {day_num} 발행 실패: `{res}`", level="error")
    else:
        print("✅ Nothing to publish today.")

def seed_to_fb():
    """Sync local book_data.json → RTDB while PRESERVING cloud state for
    `approved` and `published` flags (otherwise dashboard approvals get wiped
    every time the CI runs --seed). Scheduled dates are also preserved if
    already set in the cloud."""
    posts_ref = init_fb()
    print("🚀 Seeding local book_data.json to Firebase RTDB (state-preserving)...")
    try:
        with open('book_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        existing = posts_ref.get() or {}
        if isinstance(existing, list):
            existing = {str(p['day']): p for p in existing if p and 'day' in p}

        data_dict = {}
        for post in data:
            key = str(post['day'])
            prev = existing.get(key, {}) if isinstance(existing, dict) else {}
            # Merge: local file is the base, cloud state flags win
            merged = dict(post)
            for sticky in ("approved", "published", "scheduled_date", "scheduled_time"):
                if sticky in prev and prev[sticky] not in (None, ""):
                    merged[sticky] = prev[sticky]
            data_dict[key] = merged

        posts_ref.update(data_dict)
        print(f"✨ Successfully synced {len(data)} posts to Firebase (flags preserved).")
    except Exception as e:
        print(f"❌ Seed failed: {e}")

def _top_level_entry():
    try:
        if "--seed" in sys.argv:
            seed_to_fb()
        else:
            is_test = "--test" in sys.argv
            run_auto(test_mode=is_test)
    except Exception:
        tb = traceback.format_exc()
        print(f"💥 Unhandled exception:\n{tb}")
        # Keep alert short so it doesn't blow Slack's message limit
        head = tb.strip().splitlines()[-1][:200] if tb else "Unknown error"
        notify_slack(f"autopilot 중단: `{head}`", level="error")
        sys.exit(1)


if __name__ == "__main__":
    _top_level_entry()
