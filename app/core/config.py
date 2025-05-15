import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # 앱 정보
    APP_NAME: str = "HUFS CS-Student RAG Chatbot"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "한국외국어대학교 컴퓨터공학과 RAG 챗봇"

    # API 관련
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # 파일 경로
    VECTOR_STORE_PATH: str = "data/vector_store.json"
    DOCS_DIR: str = "data/docs"
    PROMPTS_FILE: str = "app/core/prompts.yaml"

    # 모델 설정
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    LLM_MODEL: str = "gpt-4o"

    class Config:
        env_file = ".env"


# 설정 인스턴스 생성
settings = Settings()
