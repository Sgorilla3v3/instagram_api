# Hashtag Posts Crawler WebApp (Python)

**Instagram Graph API를 이용해 특정 해시태그를 사용한 사용자 게시물을 수집하고, 사후 분석 준비까지 지원하는 웹앱**
앱 검증용 스크린샷·문서 포함

---

## 📋 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [전체 작업 과정](#전체-작업-과정)
3. [환경 및 사전 준비](#환경-및-사전-준비)
4. [설치 및 실행](#설치-및-실행)
5. [인증 & 앱 검증 요건](#인증--앱-검증-요건)
6. [코드 예시](#코드-예시)
   - 해시태그 ID 조회
   - 해시태그 기반 사용자 게시물 호출
7. [워크플로우 다이어그램](#워크플로우-다이어그램)
8. [로그 포맷 정의](#로그-포맷-정의)
9. [레이블 정의](#레이블-정의)
10. [디렉토리 구조](#디렉토리-구조)
11. [기여 가이드](#기여-가이드)
12. [라이선스](#라이선스)

---

## 1. 프로젝트 개요
- **목적**
  - Instagram Graph API로 특정 해시태그를 사용한 **사용자 게시물**(미디어) 정보를 수집
  - 수집 데이터: 날짜, 사용자 정보, 게시물 내용(caption), 미디어 링크 등
- **핵심 기능**
  - OAuth2 인증 & Long‑Lived Token 발급
  - 해시태그 ID 검색 → 페이징 크롤링 → DB 저장
  - 로그 기록(앱 검증용)
  - 추후 레이블 정의 문서화

---

## 2. 전체 작업 과정
1. 앱 등록 & OAuth 승인 요청
2. Long‑Lived Token 발급 & 저장
3. 해시태그 ID 조회
4. 해시태그 기반 사용자 게시물 호출
5. 수집 데이터(날짜·사용자·내용·링크) DB/파일 저장
6. 레이블 정의(`docs/label-definitions.md`)
7. 사후 분석(텍스트 마이닝, 네트워크 분석 등) 준비
8. 앱 검증 제출용 스크린샷·문서 준비

---

## 3. 환경 및 사전 준비
- **Python ≥ 3.9**
- **Instagram Developer Account**
  - 승인된 권한: `instagram_basic`, `pages_show_list`, `instagram_manage_insights`
- **환경변수** (`.env`)
  ```bash
  IG_CLIENT_ID=your_app_id
  IG_CLIENT_SECRET=your_app_secret
  IG_REDIRECT_URI=https://your-domain.com/auth/callback
  IG_BUSINESS_ID=your_ig_business_account_id
  IG_LONG_LIVED_TOKEN=your_long_lived_token
