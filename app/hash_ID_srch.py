import os
import requests
from dotenv import load_dotenv

load_dotenv()

INSTAGRAM_ACCOUNT_ID = os.getenv("IG_USER_ID")
ACCESS_TOKEN         = os.getenv("ACCESS_TOKEN")
HASHTAG              = os.getenv("HASHTAG")  # env에서 가져오기

def get_hashtag_id(hashtag: str) -> str:
    url = "https://graph.facebook.com/v23.0/ig_hashtag_search"
    params = {
        "user_id": INSTAGRAM_ACCOUNT_ID,
        "q": hashtag,
        "access_token": ACCESS_TOKEN,
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json().get("data", [])
    if not data:
        raise ValueError(f"No hashtag ID found for '{hashtag}'")
    return data[0]["id"]

if __name__ == "__main__":
    if not HASHTAG:
        raise RuntimeError("환경변수 HASHTAG가 설정되어 있지 않습니다.")
    try:
        tag_id = get_hashtag_id(HASHTAG)
        print(f"해시태그 '{HASHTAG}' 의 ID는: {tag_id}")
    except Exception as e:
        print("에러:", e)