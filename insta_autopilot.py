import requests
import time
import json
import os
import sys
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
            return f"Error: Request failed - {res}"
            
        print(f"⏳ Processing on Instagram... (ID: {creation_id})")
        time.sleep(60) 
        
        publish_res = requests.post(f"{base_url}/media_publish", data={
            "creation_id": creation_id,
            "access_token": ACCESS_TOKEN
        }, timeout=30).json()
        
        return publish_res.get("id")
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

    target_post = None
    # 1. Match by date
    target_post = next((p for p in posts_list if p.get("scheduled_date") == today 
                        and p.get("approved", False) 
                        and not p.get("published", False)), None)
    
    # 2. Fallback to oldest approved
    if not target_post:
        pending = [p for p in posts_list if p.get("approved", False) and not p.get("published", False)]
        if pending: target_post = sorted(pending, key=lambda x: x['day'])[0]

    if target_post:
        day_num = target_post["day"]
        print(f"🎯 Target Found: Day {day_num} ({target_post.get('hook', '')[:20]}...)")
        
        image_path = f"images/day_{day_num}.png"
        if not os.path.exists(image_path):
            print(f"⚠️ Image missing: {image_path}. Skip.")
            return

        full_caption = f"{target_post['caption']}\n\n{target_post['hashtags']}"
        
        if test_mode:
            print(f"[TEST] Would publish Day {day_num}")
            return

        public_url = get_public_url(image_path)
        if not public_url: return
        
        res = publish_to_insta(public_url, full_caption)
        print(f"Result: {res}")
        
        if res and not str(res).startswith("Error"):
            posts_ref.child(str(day_num)).update({"published": True})
            print(f"✅ RTDB Updated: Day {day_num} PUBLISHED.")
    else:
        print("✅ Nothing to publish today.")

if __name__ == "__main__":
    is_test = "--test" in sys.argv
    run_auto(test_mode=is_test)
