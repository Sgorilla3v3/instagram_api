import os
import argparse
import logging
import json
import time
import requests
from dotenv import load_dotenv

# .env 파일의 변수들을 로드
load_dotenv()

# 환경변수에서 꺼내오기
ACCESS_TOKEN  = os.getenv("ACCESS_TOKEN")
IG_USER_ID    = os.getenv("IG_USER_ID")
FIELD_PARAMS  = os.getenv("FIELD_PARAMS", "id,caption,permalink,media_type,timestamp,username")
HASHTAG_ID    = os.getenv("HASHTAG_ID")

# 로거 설정
logger = logging.getLogger("crawler")
logger.setLevel(logging.INFO)
fh = logging.FileHandler("crawler.log")
formatter = logging.Formatter('%(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

def get_hashtag_id(tag: str) -> str:
    if not IG_USER_ID or not ACCESS_TOKEN:
        raise RuntimeError("환경변수 IG_USER_ID 또는 ACCESS_TOKEN이 설정되어 있지 않습니다.")
    url = "https://graph.facebook.com/v23.0/ig_hashtag_search"
    params = {"user_id": IG_USER_ID, "q": tag, "access_token": ACCESS_TOKEN}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json().get("data", [])
    if not data:
        raise ValueError(f"해시태그 '{tag}' 에 대한 ID를 찾을 수 없습니다.")
    return data[0]["id"]

def fetch_hashtag_posts(hashtag_id: str, limit: int = 50) -> list[dict]:
    url = f"https://graph.facebook.com/v23.0/{hashtag_id}/recent_media"
    params = {"user_id": IG_USER_ID,"fields": FIELD_PARAMS, "access_token": ACCESS_TOKEN, "limit": limit}
    start = time.time()
    resp = requests.get(url, params=params)
    elapsed_ms = int((time.time() - start) * 1000)
    data = resp.json().get("data", [])
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "endpoint": resp.request.path_url,
        "status_code": resp.status_code,
        "response_time_ms": elapsed_ms,
        "items_count": len(data),
        "error": None if resp.status_code == 200 else resp.text
    }
    logger.info(json.dumps(log_entry, ensure_ascii=False))
    resp.raise_for_status()
    return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch Instagram posts by hashtag")
    parser.add_argument(
        "--hashtag", "-t",
        help="검색할 해시태그 (# 제외). env HASHTAG_ID가 있으면 생략 가능",
        required=False
    )
    parser.add_argument("--limit", "-n", type=int, default=25, help="가져올 게시물 수")
    args = parser.parse_args()

    # 1) env 에 HASHTAG_ID 가 있으면 우선 사용
    if HASHTAG_ID:
        tag_id = HASHTAG_ID
    # 2) 없으면 --hashtag 옵션으로 받은 이름을 ID 조회
    elif args.hashtag:
        tag_id = get_hashtag_id(args.hashtag)
    else:
        parser.error("HASHTAG_ID 환경변수 또는 --hashtag/-t 옵션 중 하나를 지정하세요.")

    posts = fetch_hashtag_posts(tag_id, args.limit)
## 여기에 고급 액세스 권한이 필요함
    for p in posts:
        print(
            p["timestamp"],
            p["username"],
            p["permalink"],
            (p.get("caption", "")[:40] + '...') if p.get("caption") else ''
        )


    # 디버그: 실제 posts 값이 무엇인지 출력
    print("DEBUG: posts =", posts)
    print("DEBUG: len(posts) =", len(posts))

    for p in posts:
        print(
            p["timestamp"],
            p["username"],
            p["permalink"],
            (p.get("caption", "")[:40] + '...') if p.get("caption") else ''
        )