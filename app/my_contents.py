import os
import argparse
import logging
import json
import time
import requests
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
IG_USER_ID   = os.getenv("IG_USER_ID")
FIELD_PARAMS = os.getenv(
    "FIELD_PARAMS",
    "id,caption,permalink,media_type,timestamp,username"
)
# 결과 저장 디렉터리
OUTPUT_DIR = os.getenv(
    "OUTPUT_DIR",
    "C:\\Users\\Administrator\\Desktop\\git_pre\\instagram_api\\scripts")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 로거 설정
logger = logging.getLogger("my_contents")
logger.setLevel(logging.INFO)

# 파일 핸들러
fh = logging.FileHandler(os.path.join(OUTPUT_DIR, "my_contents.log"), encoding="utf-8")
fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(fh)
# 콘솔 핸들러
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
logger.addHandler(ch)


def fetch_user_media_all(limit: int = 25) -> list[dict]:
    """
    내 비즈니스 계정의 모든 미디어를 페이징 처리하며 순차적으로 가져옵니다.
    - limit: 한 페이지당 최대 개수
    """
    base_url = f"https://graph.facebook.com/v23.0/{IG_USER_ID}/media"
    params = {
        "fields": FIELD_PARAMS,
        "access_token": ACCESS_TOKEN,
        "limit": limit,
    }

    all_posts = []
    next_url = base_url
    next_params = params

    while next_url:
        for attempt in range(3):  # 간단한 재시도 로직
            start = time.time()
            try:
                resp = requests.get(next_url, params=next_params, timeout=10)
                resp.raise_for_status()
                break
            except requests.RequestException as e:
                logger.warning(f"요청 에러, 재시도 {attempt+1}/3: {e}")
                time.sleep(2 ** attempt)
        else:
            logger.error("3번 재시도 후에도 실패하여 중단합니다.")
            return all_posts

        elapsed = int((time.time() - start) * 1000)
        payload = resp.json()
        data = payload.get("data", [])
        all_posts.extend(data)

        logger.info(
            f"페이지 요청 완료: status={resp.status_code}, "
            f"time={elapsed}ms, count_this_page={len(data)}, total={len(all_posts)}"
        )

        paging = payload.get("paging", {})
        next_url = paging.get("next")
        next_params = None  # next_url에 이미 쿼리가 포함되어 있음

    return all_posts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch all Instagram business account media with pagination"
    )
    parser.add_argument(
        "--limit", "-n",
        type=int, default=25,
        help="한 페이지당 가져올 개수 (기본: 25)"
    )
    parser.add_argument(
        "--output", "-o",
        default="all_user_media.json",
        help="저장할 JSON 파일명"
    )
    args = parser.parse_args()

    if not ACCESS_TOKEN or not IG_USER_ID:
        parser.error("환경변수 ACCESS_TOKEN 및 IG_USER_ID를 설정해주세요.")

    logger.info(f"▶️ 페이징(limit={args.limit}) 시작…")
    posts = fetch_user_media_all(args.limit)
    logger.info(f"✅ 총 {len(posts)}개 게시물 수집 완료.")

    output_path = os.path.join(OUTPUT_DIR, args.output)
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ '{output_path}' 에 저장 완료.")
    except Exception as e:
        logger.error(f"❌ JSON 저장 중 오류 발생: {e}")
