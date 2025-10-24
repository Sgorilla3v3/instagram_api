import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

def get_ig_user_id():
    # 1. 내 페이지 리스트 가져오기
    url = f"https://graph.facebook.com/v23.0/me/accounts"
    resp = requests.get(url, params={"access_token": ACCESS_TOKEN})
    resp.raise_for_status()
    pages = resp.json().get("data", [])
    if not pages:
        raise RuntimeError("❌ 연결된 Facebook Page가 없습니다.")
    
    page_id = pages[0]["id"]  # 첫 번째 페이지 사용
    print("✅ Facebook Page ID:", page_id)

    # 2. Instagram 비즈니스 계정 ID 가져오기
    url = f"https://graph.facebook.com/v23.0/{page_id}"
    params = {
        "fields": "instagram_business_account",
        "access_token": ACCESS_TOKEN
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    ig_account = resp.json().get("instagram_business_account", {})
    ig_user_id = ig_account.get("id")
    if not ig_user_id:
        raise RuntimeError("❌ 이 페이지에 연결된 Instagram 비즈니스 계정이 없습니다.")
    return ig_user_id

if __name__ == "__main__":
    ig_user_id = get_ig_user_id()
    print("✅ Instagram User ID:", ig_user_id)
