import os
from dotenv import load_dotenv
from openai import OpenAI
from app.core.config import settings

# .env 파일에서 환경 변수 로드 (한 번만 실행)
load_dotenv()

# OpenAI 클라이언트 초기화 (전역 싱글톤)
client = None


def get_openai_client():
    """
    OpenAI 클라이언트의 싱글톤 인스턴스를 반환합니다.

    Returns:
        OpenAI: OpenAI 클라이언트 인스턴스
    """
    global client
    if client is None:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return client
