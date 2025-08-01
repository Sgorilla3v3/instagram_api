# app/models.py
# Pydantic 모델 및 DB 스키마를 정의하는 곳
from pydantic import BaseModel

class Post(BaseModel):
    id: str
    caption: str = None
    like_count: int
    comments_count: int
