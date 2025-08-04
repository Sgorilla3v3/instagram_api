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
    
