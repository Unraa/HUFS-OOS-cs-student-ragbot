import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.core.config import settings
from app.api.routes import router as api_router

# FastAPI 앱 생성
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)

# API 라우터 등록
app.include_router(api_router)


# 루트 경로에 대한 리다이렉션
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>HUFS CS-Student RAG Chatbot</title>
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
        <h1>한국외국어대학교 컴퓨터공학과 RAG 챗봇</h1>
        <p>이 서비스는 한국외국어대학교 컴퓨터공학과 관련 정보를 RAG(Retrieval-Augmented Generation) 기술로 제공합니다.</p>
        
        <div class="endpoints">
            <h2>사용 가능한 엔드포인트:</h2>
            <a href="/docs">API 문서 (Swagger UI)</a>
            <a href="/redoc">API 문서 (ReDoc)</a>
            <a href="/streamlit">Streamlit 웹 인터페이스</a>
        </div>
        
        <p>자세한 정보는 API 문서를 참조하세요.</p>
    </body>
    </html>
    """


# Streamlit 앱 리다이렉션
@app.get("/streamlit")
async def streamlit_redirect():
    # 실제 배포 시에는 Streamlit 앱이 실행되는 URL로 변경
    streamlit_url = "http://localhost:8501"
    return RedirectResponse(url=streamlit_url)


if __name__ == "__main__":
    # 서버 실행
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
