import os
import sys

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import router as api_router
from app.services.embeddings import get_or_create_collection

# FastAPI 앱 생성
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # 개발 환경에서는 모든 출처 허용, 프로덕션에서는 구체적인 도메인 지정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(api_router)

# 정적 파일 마운트
app.mount("/client", StaticFiles(directory="client_web"), name="client")


# ChromaDB 초기화 - 시작 시 ChromaDB 컬렉션이 있는지 확인
@app.on_event("startup")
async def startup_db_client():
    try:
        collection = get_or_create_collection()
        print(f"ChromaDB 초기화 완료: {collection.count()}개의 청크가 로드되었습니다.")
    except Exception as e:
        print(f"ChromaDB 초기화 중 오류 발생: {str(e)}")


# 루트 경로에 대한 리다이렉션
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>한국외대 컴퓨터공학부 RAG 챗봇</title>
        <link rel="icon" href="favicon.ico" type="image/x-icon">
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            h1 {
                color: #1a73e8;
            }
            .endpoints {
                background-color: #f5f5f5;
                padding: 20px;
                border-radius: 5px;
                margin: 20px 0;
            }
            .tech-info {
                background-color: #e8f5e9;
                padding: 20px;
                border-radius: 5px;
                margin: 20px 0;
            }
            a {
                display: inline-block;
                margin: 10px 0;
                padding: 10px 15px;
                background-color: #1a73e8;
                color: white;
                text-decoration: none;
                border-radius: 4px;
            }
            a:hover {
                background-color: #0d47a1;
            }
        </style>
    </head>
    <body>
        <h1>한국외국어대학교 컴퓨터공학부 RAG 챗봇</h1>
        <p>이 서비스는 한국외국어대학교 컴퓨터공학부 관련 정보를 RAG(Retrieval-Augmented Generation) 기술로 제공합니다.</p>
        
        <div class="endpoints">
            <h2>사용 가능한 엔드포인트:</h2>
            <a href="/docs">API 문서 (Swagger UI)</a>
            <a href="/redoc">API 문서 (ReDoc)</a>
            <a href="/chat">ChatGPT 스타일 웹 인터페이스</a>
            <a href="/api/update-vector-store">벡터 저장소 업데이트 (클릭하면 바로 실행)</a>
        </div>
        
        <p>자세한 정보는 API 문서를 참조하세요.</p>
        
        <div class="tech-info">
            <h2>기술 정보:</h2>
            <ul>
                <li>벡터 데이터베이스: ChromaDB</li>
                <li>벡터 인덱싱: FAISS (HNSW)</li>
                <li>임베딩 모델: OpenAI Text Embedding</li>
                <li>생성형 AI: OpenAI GPT 모델</li>
            </ul>
        </div>
    </body>
    </html>
    """


# ChatGPT 스타일 인터페이스 제공
@app.get("/chat", response_class=HTMLResponse)
async def chat_interface():
    return RedirectResponse(url="/client/index.html")


if __name__ == "__main__":
    # 서버 실행
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
