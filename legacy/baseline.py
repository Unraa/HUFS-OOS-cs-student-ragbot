import os

import yaml
from dotenv import load_dotenv
from openai import OpenAI

# .env 파일에서 환경 변수 로드
load_dotenv()

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def load_prompts(yaml_file="code/prompts.yaml"):
    """
    YAML 파일에서 프롬프트를 로드하는 함수

    Args:
        yaml_file (str): YAML 파일 경로

    Returns:
        dict: 로드된 프롬프트
    """
    with open(yaml_file, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def call_gpt(prompt_key, system_key="default"):
    """
    GPT 모델을 호출하여 응답을 받는 함수

    Args:
        prompt_key (str): user_prompts에서 사용할 프롬프트 키
        system_key (str): system_prompts에서 사용할 프롬프트 키

    Returns:
        str: GPT 모델의 응답
    """
    try:
        # 프롬프트 로드
        prompts = load_prompts()

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompts["system_prompts"][system_key]},
                {"role": "user", "content": prompts["user_prompts"][prompt_key]},
            ],
            temperature=0.3,
            max_tokens=1000,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"에러 발생: {str(e)}")
        return None


# 사용 예시
if __name__ == "__main__":
    # 기본 정보 요청 테스트
    response = call_gpt("default")
    if response:
        print(f"기본 정보 응답: {response}")
