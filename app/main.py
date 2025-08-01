import os
from fastapi import FastAPI, Request, Depends, HTTPException
from starlette.responses import RedirectResponse
import httpx
from .crawler import get_hashtag_id, fetch_hashtag_posts

# FastAPI 앱 초기화 및 환경 변수 검증
app = FastAPI(title="Hashtag Posts Crawler")

CLIENT_ID = os.getenv("IG_CLIENT_ID")
CLIENT_SECRET = os.getenv("IG_CLIENT_SECRET")
REDIRECT_URI = os.getenv("IG_REDIRECT_URI")
BUSINESS_ID = os.getenv("IG_BUSINESS_ID")
# 단기 토큰을 ENV로 처리
SHORT_TOKEN_ENV = os.getenv("IG_SHORT_TOKEN")

@app.on_event("startup")
def validate_env():
    required = ["IG_CLIENT_ID", "IG_CLIENT_SECRET", "IG_REDIRECT_URI", "IG_BUSINESS_ID"]
    missing = [var for var in required if not os.getenv(var)]
    if missing:
        raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")

# --- OAuth: 단기 토큰 교환 & 장기 토큰 획득 ---
async def exchange_code_for_token(code: str, redirect_uri: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://graph.facebook.com/v17.0/oauth/access_token",
            params={
                "client_id": CLIENT_ID,
                "redirect_uri": redirect_uri,
                "client_secret": CLIENT_SECRET,
                "code": code,
            }
        )
        resp.raise_for_status()
        return resp.json().get("access_token")

async def get_long_lived_token(short_token: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://graph.facebook.com/v17.0/oauth/access_token",
            params={
                "grant_type": "fb_exchange_token",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "fb_exchange_token": short_token,
            }
        )
        resp.raise_for_status()
        return resp.json().get("access_token")

# --- 토큰 캐싱 및 의존성 ---
_token_cache: str = None

def cache_token(token: str):
    global _token_cache
    _token_cache = token

async def get_access_token() -> str:
    global _token_cache
    # 메모리 캐시가 없으면 ENV의 단기 토큰으로 장기 토큰 발급
    if not _token_cache:
        short_token = SHORT_TOKEN_ENV
        if not short_token:
            raise HTTPException(status_code=400, detail="No short-lived token found; authenticate via /auth/login first or set IG_SHORT_TOKEN env.")
        try:
            long_token = await get_long_lived_token(short_token)
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail="Failed to exchange long-lived token: " + exc.response.text)
        cache_token(long_token)
    return _token_cache

# --- 라우터 정의 ---
@app.get("/auth/login")
def login():
    auth_url = (
        f"https://www.facebook.com/v17.0/dialog/oauth"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=instagram_basic,pages_show_list,instagram_manage_insights"
        f"&response_type=code"
    )
    return RedirectResponse(auth_url)

@app.get("/auth/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing code in callback")

    short_token = await exchange_code_for_token(code, REDIRECT_URI)
    if not short_token:
        raise HTTPException(status_code=500, detail="Failed to obtain short-lived token")

    long_token = await get_long_lived_token(short_token)
    if not long_token:
        raise HTTPException(status_code=500, detail="Failed to obtain long-lived token")

    cache_token(long_token)
    return {"access_token": long_token}

@app.get("/crawl/{hashtag}")
async def crawl(
    hashtag: str,
    limit: int = 25,
    access_token: str = Depends(get_access_token),
):
    try:
        tag_id = await get_hashtag_id(hashtag, access_token)
        posts = await fetch_hashtag_posts(tag_id, limit, access_token)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Instagram API error: {exc.response.text}",
        )
    return {"count": len(posts), "data": posts}
