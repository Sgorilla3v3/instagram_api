# Hashtag Posts Crawler WebApp (Python)

**Instagram Graph API를 이용해 특정 해시태그를 사용한 사용자 게시물을 수집하고, 사후 분석 준비까지 지원하는 웹앱**
앱 검증용 문서·스크린샷 예시 포함

---

## 📋 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [전체 작업 과정](#전체-작업-과정)
3. [환경 및 사전 준비](#환경-및-사전-준비)
4. [설치 및 실행](#설치-및-실행)
5. [인증 & 앱 검증 요건](#인증--앱-검증-요건)
6. [코드 예시](#코드-예시)
7. [로그 포맷 정의](#로그-포맷-정의)
8. [레이블 정의](#레이블-정의)
9. [디렉토리 구조](#디렉토리-구조)
10. [기여 가이드](#기여-가이드)
11. [라이선스](#라이선스)

---

## 1. 프로젝트 개요

* **목적**

  * Instagram Graph API로 특정 해시태그를 사용한 **사용자 게시물** 정보를 수집
  * 수집 데이터: 날짜, 사용자 정보(username, ID), 게시물 내용(caption), 미디어 링크(permalink), 타입 등
    
* **핵심 기능**

  * OAuth2 인증 & Long-Lived Token 발급(사전작업)
  * 해시태그 ID 검색 → 페이징 크롤링 → DB/파일 저장
  * 앱 검증용 로그 기록
  * 추후 레이블 정의 문서화

---

## 2. 전체 작업 과정

1. 앱 등록 & OAuth 승인 요청(사전작업)
2. Long-Lived Token 발급 & 저장(사전작업)
3. 해시태그 ID 조회
4. 해시태그 기반 사용자 게시물 호출
5. 수집 데이터(날짜·사용자·내용·링크·타입) DB/파일 저장
6. 레이블 정의 문서화 (`docs/label-definitions.md`)
7. 사후 분석(텍스트 마이닝, 네트워크 분석 등) 준비
8. 앱 검증 제출용 스크린샷·문서 준비

---

## 3. 환경 및 사전 준비

* **Python ≥ 3.9**
* **Instagram Developer Account**

  * 필요 권한: `instagram_basic`, `pages_show_list`, `instagram_manage_insights`, `business_management`, `page_read_engagement`, `pages_read_user_content`
* **환경변수** (`.env` 또는 CI 환경 설정)

  ```bash
  PAGE_ID =your_page_id
  ACCESS_TOKEN =Long_lived_token
  HASHTAG=hashtag_str
  API_VERSION =v23.0
  IG_USER_ID =your_business_ID 
  HASHTAG_ID =hashtag_ID
  FIELD_PARAM=id,caption,timestamp,permalink,media_url,owner{id,username},like_count,comments_count
  OUTPUT_DIR =C:\\Users\\Administrator\\Desktop\\git_pre\\instagram_api\\scripts
  ```

---

## 4. 설치 및 실행

```bash
git clone https://github.com/Sgorilla3v3/instagram_api.git
cd instagram_api

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# .env에 환경변수 설정

uvicorn app.main:app --reload
```
실제 서버를 띄우려면 아래 순서대로 진행하시면 됩니다.

1. **프로젝트 클론 및 디렉터리 진입**

   ```bash
   git clone <repo-url>
   cd <repo-root>
   ```

2. **가상환경 생성 및 활성화**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate      # macOS/Linux
   .venv\Scripts\activate         # Windows
   ```

3. **의존성 설치**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **환경 변수 설정**
   프로젝트 루트에 `.env` 파일을 만들고 `.env.example`의 템플릿을 복사한 뒤, 다음 값을 채워 넣습니다.

   ```dotenv
   IG_CLIENT_ID=…
   IG_CLIENT_SECRET=…
   IG_REDIRECT_URI=…
   IG_BUSINESS_ID=…
   IG_SHORT_TOKEN=…
   ```


## 5. 인증 & 앱 검증 요건

* **OAuth2 흐름**

  1. `/auth/login` → Instagram 동의 화면
  2. `/auth/callback` → `code` 수신 → 토큰 교환
* **앱 검증용 문서**

  * 이 README.md
  * `docs/app-review.md` (정책 준수 체크리스트)
  * 주요 Postman 요청·응답 스크린샷

---

## 6. 코드 예시

### 6.1 해시태그 ID 조회

```python
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
```

### 6.2 해시태그 기반 사용자 게시물 호출

```python
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
```

---

## 7. 로그 포맷 정의

앱 검증용 로그 예시(JSON)

```json
{
  "timestamp": "2025-07-28T18:00:00+09:00",
  "endpoint": "/17841562420007458/recent_media",
  "status_code": 200,
  "response_time_ms": 150,
  "items_count": 25,
  "error": null
}
```

| 필드                 | 설명               |
| ------------------ | ---------------- |
| `timestamp`        | ISO8601 형식 요청 시각 |
| `endpoint`         | 호출 엔드포인트         |
| `status_code`      | HTTP 응답 코드       |
| `response_time_ms` | 응답 소요 시간 (밀리초)   |
| `items_count`      | 반환된 아이템 개수       |
| `error`            | 오류 메시지 (실패 시)    |

---

## 8. 레이블 정의


| 레이블                    | 타입       | 설명                                     | API 필드                        |
| ---------------------- | -------- | -------------------------------------- | ----------------------------- |
| `id`                   | string   | 게시물 고유 식별자                             | `id`                          |
| `username`             | string   | 게시물 작성자 계정명                            | `username`                    |
| `user_id`              | string   | 게시물 작성자 계정의 비즈니스 계정 ID                 | `ig_id` (비즈니스 API)            |
| `caption`              | string   | 게시물 캡션 텍스트                             | `caption`                     |
| `media_type`           | enum     | 미디어 타입 (IMAGE, VIDEO, CAROUSEL\_ALBUM) | `media_type`                  |
| `media_url`            | URL      | 이미지 혹은 비디오 파일의 URL                     | `media_url`                   |
| `permalink`            | URL      | 게시물 고유 링크                              | `permalink`                   |
| `thumbnail_url`        | URL      | 비디오 미디어의 경우 썸네일 이미지 URL                | `thumbnail_url`               |
| `timestamp`            | datetime | 게시물 업로드 시간 (ISO 8601 형식)               | `timestamp`                   |
| `like_count`           | integer  | 게시물 좋아요 수 (비즈니스 계정에서만 조회 가능)           | `like_count`                  |
| `comments_count`       | integer  | 게시물 댓글 수 (비즈니스 계정에서만 조회 가능)            | `comments_count`              |
| `children`             | list     | 캐로셀(여러 미디어) 게시물의 자식 미디어 목록             | `children.data`               |
| `location`             | object   | 게시물 위치 정보 (장소 ID, 이름, 위도/경도 등)         | `location`                    |
| `insights.impressions` | integer  | 게시물 도달 수 (비즈니스 계정 전용, 인사이트 엔드포인트 사용)   | `insights.metric=impressions` |
| `insights.reach`       | integer  | 게시물 조회 수 (비즈니스 계정 전용)                  | `insights.metric=reach`       |
| `insights.engagement`  | integer  | 게시물 참여 수 (비즈니스 계정 전용)                  | `insights.metric=engagement`  |

---

## 9. 디렉토리 구조

```
.
├── app/
│   ├── hash_ID_posts.py          # hashtag_ID로 게시물 검색(ex. 청도혁신센터)
│   ├── hash_ID_srch.py          # 원하는 hashtag_ID 검색
│   ├── my_contents.py       # 내 게시물 불러와서 json 저장(고급액세스는 필요없으나 데이터 확보에 필요한 작업)
│   └── models.py  # 추후 데이터 양이 많아지거나 자동화, 웹앱화시 데이터 용량 확대를 위한 스키마 정의파트
├── docs/
│   └──  app-review.md    # 앱 검증용 체크리스트
├── scripts/             # 사후 분석 스크립트 모음
├── tests/               # 유닛 테스트
├── .env                 # 환경변수 템플릿 파일
├── requirements.txt     # Python 의존성 목록
├── .gitignore     # .env등 환경변수를 자동으로 공유하지 않도록 설정
└── README.md     # 프로젝트 전반 문서
```


## 10. 기여 가이드


### 1) 시작하기

```bash
# 저장소 포크 & 클론
git clone https://github.com/내_계정/instagram_api.git
cd instagram_api

# upstream 설정
git remote add upstream https://github.com/Sgorilla3v3/instagram_api.git
git fetch upstream && git checkout main && git merge upstream/main
```

### 2) 브랜치 전략

* `main`: 배포용 안정 브랜치
* `develop`: 개발 통합 브랜치 (선택)
* 기능 브랜치: `feature/{이슈번호}-{설명}`
* 버그 브랜치: `bugfix/{이슈번호}-{설명}`

### 3) 코드 스타일

* Python: Black, flake8 사용
* Commit 메시지: `[feat|fix|docs|test|refactor] #이슈번호 요약`

### 4) Pull Request

1. Fork → 브랜치 생성 → 작업
2. Commit & Push
3. GitHub에서 PR 생성 (Base: main, Compare: feature/\*)
4. 리뷰 반영 → Merge

### 5) 이슈 작성

* 템플릿: Bug Report / Feature Request
* 최소 정보: 재현 방법, 환경, 기대 결과 vs 실제 결과

### 6) 테스트

```bash
pytest --cov=app tests/
```

### 7) 코드 오너

`.github/CODEOWNERS`에 담당자 지정 가능

---

## 11. 라이선스

MIT © 2025 Jonathan Seong





