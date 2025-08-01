# app/models.py
# Pydantic 모델 및 DB 스키마를 정의하는 곳
from pydantic import BaseModel
from datetime import datetime

class Post(BaseModel):
    id: str
    caption: str = None
    username: str
    timestamp: datetime  # 게시물 업로드 시간
    like_count: int
    comments_count: int
    permalink: str
    media_type: str  # IMAGE, VIDEO, CAROUSEL_ALBUM 등
