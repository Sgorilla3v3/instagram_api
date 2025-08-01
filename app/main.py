# app/main.py
import os
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .auth import router as auth_router
from .crawler import router as crawler_router

# FastAPI 앱 초기화
app = FastAPI(title="Hashtag Posts Crawler")

# CORS (필요 시 설정)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(crawler_router, prefix="/crawl", tags=["crawler"])
