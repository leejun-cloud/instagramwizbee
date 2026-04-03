import requests
import time
import os

# Configuration (from insta_autopilot.py)
ACCOUNT_ID = "17841427998042847"
ACCESS_TOKEN = "REDACTED_INSTA_TOKEN"
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
        print(f"Error hosting file {file_path}: {e}")
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
        return f"Error Container: {res}"
    
    # Processing wait
    print(f"⏳ Waiting for Instagram to process {image_url}... (ID: {creation_id})")
    time.sleep(30) 
    
    # 2. Publish
    publish_res = requests.post(f"{base_url}/media_publish", data={
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN
    }).json()
    return publish_res.get("id")

quotes = [
    "직원들이 내부 위험을 견뎌야 하는 조직은 외부 위험에 대처하기 어려워진다.",
    "목표실적을 달성하기위해 직원들을 희생시켜도 괜찮다고 생각하는 리더들은 그렇게 했을때 일련의 결과가 어떻게 나타날지까지 고려해야 한다.",
    "진정한 리더는 마지막에 먹는다",
    "신뢰란 기계에 칠하는 윤활유와 같다. 신뢰는 마찰을 줄이고 더 높은 성과를 내기에 적합한 환경을 만든다.",
    "사람들에게 시간과 에너지를 쏟으라. 신뢰를 형성하는데 시간이 걸리며 그 속도를 빠르게 해주는 앱 같은 건 없다",
    "가까워지는 것이 먼저다. 적들은 싸우지만 친구들은 협력한다",
    "인간이 5만년 동안 번영한 이유는 자시 자신이 아니라 다른 사람을 섬겼기 때문이다"
]

if __name__ == "__main__":
    results = []
    for i in range(1, 8):
        file_path = f"/tmp/card_{i}.png"
        caption = quotes[i-1] + "\n\n#위즈비 #리더십 #신뢰 #카드뉴스"
        
        print(f"Processing Card {i}...")
        public_url = get_public_url(file_path)
        if public_url:
            print(f"Hosted at: {public_url}")
            media_id = publish_to_insta(public_url, caption)
            print(f"Published! Media ID: {media_id}")
            results.append((public_url, media_id))
        else:
            print(f"Failed to host Card {i}")
    
    with open("/tmp/upload_results.txt", "w") as f:
        for url, mid in results:
            f.write(f"{url} | {mid}\n")
