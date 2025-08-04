import os
import requests

INSTAGRAM_ACCOUNT_ID = os.getenv("IG_BUSINESS_ID")
ACCESS_TOKEN         = os.getenv("IG_LONG_LIVED_TOKEN")

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