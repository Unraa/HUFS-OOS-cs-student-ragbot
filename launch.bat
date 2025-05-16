@echo off
REM =====================================================================
REM 실행 방법:
REM 1. 명령 프롬프트(cmd)에서: launch.bat
REM 2. 윈도우 탐색기에서: 파일을 더블클릭
REM =====================================================================
echo =========================================
echo 한국외국어대학교 컴퓨터공학과 RAG 챗봇 시작
echo =========================================

REM 현재 디렉토리를 PYTHONPATH에 추가
set PYTHONPATH=%PYTHONPATH%;%CD%

REM ChromaDB 디렉토리 확인
if not exist "data\chroma_db" (
    echo ChromaDB 디렉토리가 없습니다. 자동으로 생성됩니다.
    mkdir data\chroma_db
)

REM FastAPI 서버 실행
echo FastAPI 서버 시작 중...
start /B uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo 서비스가 시작되었습니다.
echo FastAPI: http://localhost:8000
echo FastAPI 문서: http://localhost:8000/docs
echo 챗봇 인터페이스: http://localhost:8000/chat
echo 벡터 저장소 업데이트: http://localhost:8000/api/update-vector-store
echo ----------------------------------------
echo 종료하려면 이 창을 닫으세요.

REM 사용자 입력을 대기
pause 