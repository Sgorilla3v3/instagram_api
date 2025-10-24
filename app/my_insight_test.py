import os
import logging
import json
import time
import requests
from dotenv import load_dotenv
from tqdm import tqdm

# .env 파일 로드
load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
FIELD_PARAMS = os.getenv("FIELD_PARAMS")

# metrics
INSIGHT_METRICS       = os.getenv("INSIGHT_METRICS")
INSIGHT_METRICS_STORY = os.getenv("INSIGHT_METRICS_STORY")
INSIGHT_METRICS_REELS = os.getenv("INSIGHT_METRICS_REELS")
INSIGHT_METRICS_VIDEO = os.getenv("INSIGHT_METRICS_VIDEO")

OUTPUT_DIR = os.getenv("OUTPUT_DIR")
os.makedirs(OUTPUT_DIR, exist_ok=True)

INPUT_FILE = "scripts/all_user_media_with_insights_copy.json"   # 📌 고정 경로
OUTPUT_FILE = "retry_media_with_insights.json"                 # 결과 파일명 고정

# 로거 설정
logger = logging.getLogger("ig_contents")
logger.setLevel(logging.INFO)
fh = logging.FileHandler(os.path.join(OUTPUT_DIR, "retry_media.log"), encoding="utf-8")
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
    else:
        return INSIGHT_METRICS


def fetch_post_info(media_id: str) -> dict:
    """특정 media_id 기본 정보 조회"""
    url = f"https://graph.facebook.com/v23.0/{media_id}"
    params = {"fields": FIELD_PARAMS, "access_token": ACCESS_TOKEN}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()


def fetch_insights(media_id: str, metrics: str) -> dict:
    """특정 미디어 insights 조회"""
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
    if not ACCESS_TOKEN:
        raise SystemExit("환경변수 ACCESS_TOKEN을 설정해주세요.")

    # 📌 JSON에서 media_id 목록 불러오기
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    media_ids = [item["id"] for item in data if "id" in item]
    logger.info(f"📂 파일에서 {len(media_ids)}개 media_id 로드 완료")

    results = []
    for mid in tqdm(media_ids, desc="📊 미디어 insights 재시도", unit="media"):
        try:
            post_info = fetch_post_info(mid)
            metrics = get_metrics_for_post(post_info)
            insights = fetch_insights(mid, metrics)
            post_info["insights"] = insights.get("data", insights.get("error"))
            results.append(post_info)
            time.sleep(0.3)  # rate limit 방지
        except Exception as e:
            logger.error(f"❌ {mid} 처리 실패: {e}")
            results.append({"id": mid, "insights": {"error": str(e)}})

    # 📌 결과 저장
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    logger.info(f"💾 '{output_path}' 저장 완료")
