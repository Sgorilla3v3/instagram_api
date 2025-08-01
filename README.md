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

  * OAuth2 인증 & Long-Lived Token 발급
  * 해시태그 ID 검색 → 페이징 크롤링 → DB/파일 저장
  * 앱 검증용 로그 기록
  * 추후 레이블 정의 문서화

---

## 2. 전체 작업 과정

1. 앱 등록 & OAuth 승인 요청
2. Long-Lived Token 발급 & 저장
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
  IG_CLIENT_ID=your_app_id
  IG_CLIENT_SECRET=your_app_secret
  IG_REDIRECT_URI=https://your-domain.com/auth/callback
  IG_BUSINESS_ID=your_ig_business_account_id
  IG_LONG_LIVED_TOKEN=your_long_lived_token
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
   # (선택) 수동 단기 토큰
   IG_SHORT_TOKEN=…
   ```

5. **Uvicorn으로 서버 실행**
   FastAPI 앱(`app/main.py` 안의 `app` 객체)을 `uvicorn`으로 구동합니다.

   ```bash
   uvicorn app.main:app \
     --host 0.0.0.0 \
     --port 8000 \
     --reload
   ```

   * `--reload` 옵션을 주면 코드 변경 시 자동 재시작됩니다.

6. **엔드포인트 확인**

   * OAuth 로그인:
     `http://localhost:8000/auth/login`
   * 콜백(토큰 발급):
     `http://localhost:8000/auth/callback?code=<발급된 code>`
   * 해시태그 크롤링:
     `http://localhost:8000/crawl/<hashtag>?limit=10`


이제 `localhost:8000/docs` 에 접속하시면 Swagger UI로 자동 생성된 API 문서를 통해도 각 엔드포인트를 테스트해 보실 수 있습니다.

---

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
import argparse
import logging
import json
import time
import requests

# 로거 설정
logger = logging.getLogger("crawler")
logger.setLevel(logging.INFO)
fh = logging.FileHandler("crawler.log")
formatter = logging.Formatter('%(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

# fetch_hashtag_posts 함수는 ACCESS_TOKEN을 환경변수로부터 읽어 옵니다

def fetch_hashtag_posts(hashtag_id: str, limit: int = 50) -> list[dict]:
    url = f"https://graph.facebook.com/v23.0/{hashtag_id}/recent_media"
    params = {
        "fields": "id,caption,permalink,media_type,timestamp,username",
        "access_token": ACCESS_TOKEN,
        "limit": limit,
    }
    start = time.time()
    resp = requests.get(url, params=params)
    elapsed_ms = int((time.time() - start) * 1000)
    data = resp.json().get("data", [])
    # 로그 기록
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
    parser.add_argument("hashtag", help="검색할 해시태그 (# 제외)")
    parser.add_argument("--limit", type=int, default=25, help="가져올 게시물 수")
    args = parser.parse_args()

    # 사용자 입력으로 해시태그 ID 조회
    tag_id = get_hashtag_id(args.hashtag)
    posts = fetch_hashtag_posts(tag_id, args.limit)

    for p in posts:
        print(
            p["timestamp"],
            p["username"],
            p["permalink"],
            (p.get("caption","")[:40] + '...') if p.get("caption") else ''
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

`docs/label-definitions.md` 문서에 상세 정의 예정이며, 인스타그램 Graph API 문서를 참고하여 초기 예시 레이블을 아래와 같이 제안합니다.

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
│   ├── main.py          # FastAPI 서버 진입점
│   ├── auth.py          # OAuth2 로직
│   ├── crawler.py       # get_hashtag_id, fetch_hashtag_posts
│   └── models.py        # Pydantic & DB 모델
├── docs/
│   ├── app-review.md    # 앱 검증용 체크리스트
│   └── label-definitions.md  # 레이블 분류 기준 정의
├── scripts/             # 사후 분석 스크립트 모음
├── tests/               # 유닛 테스트
├── .env                 # 환경변수 템플릿 파일
├── requirements.txt     # Python 의존성 목록
└── README.md     # 프로젝트 전반 문서
```
* **각 디렉토리 및 파일 설명**:
  * app/: 애플리케이션 코어 로직이 위치하는 폴더입니다.
  * main.py: FastAPI 애플리케이션 인스턴스 생성 및 라우터 등록
  * auth.py: OAuth2 인증 처리(로그인·콜백) 관련 기능
  * crawler.py: 해시태그 ID 조회 및 사용자 게시물 크롤링 함수 구현
  * models.py: Pydantic 모델 및 데이터베이스 스키마 정의

* **docs/**: 프로젝트 문서화를 위한 디렉토리입니다.
  * app-review.md: Instagram 앱 검증 시 제출할 체크리스트 및 스크린샷 가이드
  * label-definitions.md: 수집 데이터에 적용할 레이블(분류 기준) 상세 정의

* **scripts/**: 사후 분석을 위한 스크립트가 위치합니다.
  * 예: 언급량 집계(aggregate.py), 텍스트 네트워크 생성(text_network.py)

* **tests/**: 테스트 코드 디렉토리입니다.
  * 유닛 테스트, API 통합 테스트 및 Mock 활용 예제 포함

* **.env.example**: 환경변수 설정 예시 파일로, 실제 .env 파일을 생성할 때 참고합니다.

* **requirements.txt**: 프로젝트에서 사용하는 Python 패키지 목록과 버전 정보를 관리합니다.

* **README.md**: 프로젝트 개요, 사용법, 코드 예시, 기여 가이드 등 주요 문서를 포함한 최상위 문서입니다.
---

## 10. 기여 가이드

아래는 `CONTRIBUTING.md` 작성 예시로, 저장소 루트에 파일을 추가하시고 링크해주세요.

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





