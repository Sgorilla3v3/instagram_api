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

