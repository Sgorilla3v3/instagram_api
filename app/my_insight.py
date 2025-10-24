import os
import argparse
import logging
import json
import time
import requests
from dotenv import load_dotenv
from typing import List, Dict, Any
from tqdm import tqdm   # 진행바 라이브러리

# .env 파일 로드
load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
IG_USER_ID   = os.getenv("IG_USER_ID")
FIELD_PARAMS = os.getenv("FIELD_PARAMS")

# metrics를 env에서 읽고 없으면 기본값 사용
INSIGHT_METRICS       = os.getenv("INSIGHT_METRICS")
INSIGHT_METRICS_STORY = os.getenv("INSIGHT_METRICS_STORY")
INSIGHT_METRICS_REELS = os.getenv("INSIGHT_METRICS_REELS")
INSIGHT_METRICS_VIDEO = os.getenv("INSIGHT_METRICS_VIDEO")

OUTPUT_DIR = os.getenv("OUTPUT_DIR")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 로거 설정
logger = logging.getLogger("ig_contents")
logger.setLevel(logging.INFO)
fh = logging.FileHandler(os.path.join(OUTPUT_DIR, "my_contents.log"), encoding="utf-8")
fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(fh)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
logger.addHandler(ch)


def get_metrics_for_post(post: dict) -> str:
    """미디어 타입에 따라 metrics 세트 반환"""
    mtype = post.get("media_type")
    product = post.get("media_product_type")

    if product == "STORY":
        return INSIGHT_METRICS_STORY
    elif product == "REELS":
        return INSIGHT_METRICS_REELS
    elif mtype == "VIDEO":
        return INSIGHT_METRICS_VIDEO
    else:  # IMAGE, CAROUSEL_ALBUM 등
        return INSIGHT_METRICS


def fetch_user_media_all(limit: int = 100) -> List[Dict[str, Any]]:
    """
    Instagram 비즈니스 계정의 모든 미디어를 페이징 처리하며 가져오기
    """
    base_url = f"https://graph.facebook.com/v23.0/{IG_USER_ID}/media"
    params = {
        "fields": FIELD_PARAMS,
        "access_token": ACCESS_TOKEN,
        "limit": limit,
    }

    all_posts = []
    next_url, next_params = base_url, params

    while next_url:
        for attempt in range(3):
            try:
                if next_params:
                    resp = requests.get(next_url, params=next_params, timeout=10)
                else:
                    resp = requests.get(next_url, timeout=10)

                if resp.status_code == 429:
                    logger.warning("⚠️ Rate limit 초과 → 60초 대기 후 재시도")
                    time.sleep(60)
                    continue

                resp.raise_for_status()
                break
            except requests.RequestException as e:
                logger.warning(f"요청 에러, 재시도 {attempt+1}/3: {e}")
                time.sleep(2 ** attempt)
        else:
            logger.error("3번 재시도 후에도 실패 → 중단")
            return all_posts

        payload = resp.json()
        data = payload.get("data", [])
        all_posts.extend(data)

        logger.info(f"페이지 수집 완료: {len(data)}개, 누적 {len(all_posts)}개")

        paging = payload.get("paging", {})
        next_url = paging.get("next")
        next_params = None

    return all_posts


def fetch_insights(media_id: str, metrics: str) -> dict:
    """
    특정 미디어의 insights 데이터 가져오기
    """
    url = f"https://graph.facebook.com/v23.0/{media_id}/insights"
    params = {"metric": metrics, "access_token": ACCESS_TOKEN}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        logger.error(f"❌ insights 요청 실패 (media_id={media_id}): {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch all Instagram business account media with insights"
    )
    parser.add_argument(
        "--output", "-o",
        default="all_user_media_with_insights.json",
        help="저장할 JSON 파일명"
    )
    args = parser.parse_args()

    if not ACCESS_TOKEN or not IG_USER_ID:
        parser.error("환경변수 ACCESS_TOKEN 및 IG_USER_ID를 설정해주세요.")

    logger.info("▶️ 전체 미디어 수집 시작…")
    posts = fetch_user_media_all()
    logger.info(f"✅ 총 {len(posts)}개 미디어 수집 완료")

    # 각 미디어 insights 붙이기 (진행바 출력)
    results = []
    for post in tqdm(posts, desc="📊 미디어 insights 수집", unit="media"):
        metrics = get_metrics_for_post(post)
        insights = fetch_insights(post["id"], metrics)
        post["insights"] = insights.get("data", insights.get("error"))
        results.append(post)
        time.sleep(0.3)  # rate limit 방지

    # JSON 저장
    output_path = os.path.join(OUTPUT_DIR, args.output)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 '{output_path}' 저장 완료")
    except Exception as e:
        logger.error(f"❌ JSON 저장 오류: {e}")
