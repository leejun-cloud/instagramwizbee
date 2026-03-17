import requests
import json

ACCESS_TOKEN = "REDACTED_INSTA_TOKEN"
ACCOUNT_ID = "17841427998042847"

def check_media():
    url = f"https://graph.instagram.com/v23.0/{ACCOUNT_ID}/media"
    params = {
        "access_token": ACCESS_TOKEN,
        "fields": "id,timestamp,caption"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            media_data = response.json()
            print("Media found:", json.dumps(media_data, indent=2, ensure_ascii=False))
        else:
            print(f"Error fetching media: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Exception: {e}")

def check_account():
    url = f"https://graph.instagram.com/v23.0/{ACCOUNT_ID}"
    params = {
        "access_token": ACCESS_TOKEN,
        "fields": "username,name"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            print("Account info:", response.json())
        else:
            print(f"Error fetching account: {response.status_code}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    check_account()
    check_media()
