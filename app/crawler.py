# app/crawler.py (기존)
from fastapi import APIRouter, Depends, HTTPException
import httpx
from .auth import get_access_token
from .crawler_logic import get_hashtag_id, fetch_hashtag_posts  # 내부 로직 분리

router = APIRouter()

@router.get("/{hashtag}")
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

# app/crawler_logic.py
import httpx

async def get_hashtag_id(tag: str, token: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://graph.facebook.com/ig_hashtag_search",
            params={"user_id": token, "q": tag},
        )
        resp.raise_for_status()
        return resp.json()["data"][0]["id"]

async def fetch_hashtag_posts(tag_id: str, limit: int, token: str) -> list:
    async with httpx.AsyncClient() as client:
        params = {"user_id": token, "fields": "id,caption,like_count,comments_count", "limit": limit}
        resp = await client.get(f"https://graph.facebook.com/{tag_id}/recent_media", params=params)
        resp.raise_for_status()
        return resp.json().get("data", [])
