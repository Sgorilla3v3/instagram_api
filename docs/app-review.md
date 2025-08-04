# Instagram App Review Checklist

이 문서는 `Sgorilla3v3/instagram_api` 프로젝트의 Instagram Graph API 앱 검증(submission) 절차를 위해 준비해야 할 정책 준수 체크리스트입니다.

---

## 1. 앱 정보

* **앱 이름(App Name)**: Instagram Posts Crawler
* **비즈니스 계정(Business Account)**: Instagram 비즈니스 계정 ID 등록 완료
* **앱 아이콘(App Icon)**: 1024×1024px, PNG

## 2. OAuth Redirect URI

* **등록된 URI**: `https://cmz054.kr/auth/callback` (ngrok 또는 실제 도메인)
* Facebook 개발자 대시보드의 **Valid OAuth Redirect URIs**에 정확히 등록

## 3. 데이터 사용 정책(Data Usage)

* **사용 권한(Scopes)**:

  * `instagram_basic`
  * `pages_show_list`
  * `business_management`
  * `instagram_manage_insights` (해시태그 인사이트 조회시)
  * `pages_read_engagement`
  * `pages_read_user_content`
  * `Instagram_public_content_access` (고급엑세스 요청중)
<img width="988" height="775" alt="image" src="https://github.com/user-attachments/assets/5dd3265c-4ebc-41d7-8022-c6ab84ef6c38" />

* **데이터 저장 및 보관**:

  * 수집한 게시물 데이터(캡션, 메타정보)를 DB에 암호화 저장
  * 사용자가 요청한 데이터만 저장(명시적 동의 필요 없음)
* **데이터 삭제 정책**:

  * Facebook 인증 계정 연결 해제 시 해당 계정 관련 데이터 자동 삭제

## 4. 개인정보 처리 방침(Privacy Policy)

* **URL**: `https://cmz054.kr/?mode=privacy`
* 주요 항목:

  * 수집하는 정보: 게시물 메타정보(텍스트, 링크, 타임스탬프 등)
  * 이용 목적: 사용자 요청 기반 데이터 수집 및 분석
  * 제3자 제공 여부: 없음
  * 데이터 보관 기간: 30일 후 자동 삭제

## 5. 서비스 약관(Terms of Service)

* **URL**: `https://cmz054.kr/?mode=policy`
* 사용 약관에 App Review 승인 후에도 사용 가능한 범위 명시

## 6. 스크린샷 및 동작 영상

1. **OAuth2 인증 흐름**

   * 로그인 화면 → 동의 → 콜백 URL (주소창 포함)
2. **Long-Lived Token 발급**

   * Postman 또는 curl 요청/응답 화면
3. **해시태그 ID 조회**

   * `/ig_hashtag_search` 요청 파라미터 및 응답 스크린샷
4. **게시물 호출 및 로그 기록**

   * `/hashtag_id/recent_media` 호출 응답 일부 + `hashtag_contents.log` JSON 기록 예시

## 7. 버전 및 배포(Versioning & Deployment)

* **버전 태깅**: GitHub Release 태그(`v1.0.0` 등) 사용
* **배포 환경**: nginx + Uvicorn (HTTPS 적용)

## 8. 추가 검증 자료(Additional)

* **Postman Collection**: `.postman_collection.json` 첨부
* **README.md**: 프로젝트 개요 및 사용법
* **CONTRIBUTING.md**: 기여 가이드
* **LICENSE**: MIT 라이선스

---

### 완료 기준(Definition of Done)

* 위 1\~8 항목에 필요한 문서, 스크린샷, URL 등록 완료
* Facebook 개발자 대시보드에서 모든 필수 필드(아이콘, 개인정보 처리방침 등) 입력 완료
* Test User 계정으로 실제 인증 및 API 호출 성공 확인
