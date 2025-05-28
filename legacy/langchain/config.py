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

    # ChromaDB 설정
    CHROMA_DB_DIR: str = "data/chroma_db"
    CHROMA_COLLECTION_NAME: str = "hufs_cs_docs"

    # 모델 설정
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    LLM_MODEL: str = "gpt-4o"

    # Langchain 설정
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    RETRIEVAL_K: int = 5
    TEMPERATURE: float = 0.3
    MAX_TOKENS: int = 1000

    class Config:
        env_file = ".env"

    def validate_api_key(self):
        """OpenAI API 키 유효성 검사"""
        if not self.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요."
            )
        if not self.OPENAI_API_KEY.startswith("sk-"):
            raise ValueError("유효하지 않은 OpenAI API 키 형식입니다.")
        return True


# 설정 인스턴스 생성
settings = Settings()

# API 키 검증 (선택적)
try:
    settings.validate_api_key()
    print("✓ OpenAI API 키가 올바르게 설정되었습니다.")
except ValueError as e:
    print(f"⚠️  API 키 설정 오류: {e}")
    print("Langchain RAG 시스템이 제대로 작동하지 않을 수 있습니다.")
