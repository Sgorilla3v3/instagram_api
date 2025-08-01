# app/auth.py
import os
from fastapi import APIRouter, Request, Depends, HTTPException
from starlette.responses import RedirectResponse
import httpx

router = APIRouter()

CLIENT_ID = os.getenv("IG_CLIENT_ID")
CLIENT_SECRET = os.getenv("IG_CLIENT_SECRET")
REDIRECT_URI = os.getenv("IG_REDIRECT_URI")
SHORT_TOKEN_ENV = os.getenv("IG_SHORT_TOKEN")

# 메모리 캐시
_token_cache: str = None

def cache_token(token: str):
    global _token_cache
    _token_cache = token

async def exchange_code_for_token(code: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://graph.facebook.com/v23.0/oauth/access_token",
            params={
                "client_id": CLIENT_ID,
                "redirect_uri": REDIRECT_URI,
                "client_secret": CLIENT_SECRET,
                "code": code,
            }
        )
        resp.raise_for_status()
        return resp.json().get("access_token")

async def get_long_lived_token(short_token: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://graph.facebook.com/v23.0/oauth/access_token",
            params={
                "grant_type": "fb_exchange_token",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "fb_exchange_token": short_token,
            }
        )
        resp.raise_for_status()
        return resp.json().get("access_token")

async def get_access_token() -> str:
    global _token_cache
    if not _token_cache:
        short_token = SHORT_TOKEN_ENV
        if not short_token:
            raise HTTPException(
                status_code=400,
                detail="No short-lived token; set IG_SHORT_TOKEN or authenticate via /auth/login",
            )
        long_token = await get_long_lived_token(short_token)
        cache_token(long_token)
    return _token_cache

@router.get("/login")
def login():
    auth_url = (
        f"https://www.facebook.com/v23.0/dialog/oauth"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=instagram_basic,pages_show_list,instagram_manage_insights"
        f"&response_type=code"
    )
    return RedirectResponse(auth_url)

@router.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing code in callback")

    short_token = await exchange_code_for_token(code)
    if not short_token:
        raise HTTPException(status_code=500, detail="Failed to obtain short-lived token")

    long_token = await get_long_lived_token(short_token)
    if not long_token:
        raise HTTPException(status_code=500, detail="Failed to obtain long-lived token")

    cache_token(long_token)
    return {"access_token": long_token}
