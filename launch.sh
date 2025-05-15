#!/bin/bash

# 터미널 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 현재 디렉토리를 PYTHONPATH에 추가
export PYTHONPATH=$PYTHONPATH:$(pwd)

echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}한국외국어대학교 컴퓨터공학과 RAG 챗봇 시작${NC}"
echo -e "${BLUE}=========================================${NC}"

# Streamlit과 FastAPI를 백그라운드에서 실행
echo -e "${YELLOW}Streamlit 앱 시작 중...${NC}"
streamlit run app/web/streamlit_app.py --server.port=8503 &
STREAMLIT_PID=$!

# 잠시 대기
sleep 2

echo -e "${YELLOW}FastAPI 서버 시작 중...${NC}"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
FASTAPI_PID=$!

# 종료 핸들링
trap "kill $STREAMLIT_PID $FASTAPI_PID; exit" SIGINT SIGTERM

echo -e "${GREEN}모든 서비스가 시작되었습니다.${NC}"
echo -e "${YELLOW}Streamlit UI:${NC} http://localhost:8503"
echo -e "${YELLOW}FastAPI:${NC} http://localhost:8000"
echo -e "${YELLOW}FastAPI 문서:${NC} http://localhost:8000/docs"
echo -e "${BLUE}----------------------------------------${NC}"
echo -e "${YELLOW}종료하려면 Ctrl+C를 누르세요.${NC}"

# 프로세스가 종료될 때까지 대기
wait 