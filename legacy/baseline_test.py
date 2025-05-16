import os
from openai import OpenAI
from dotenv import load_dotenv
import yaml

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


def call_gpt(user_input, system_key="default"):
    """
    GPT 모델을 호출하여 응답을 받는 함수

    Args:
        user_input (str): 사용자 입력 메시지
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
                {"role": "user", "content": user_input},
            ],
            temperature=0.3,
            max_tokens=1000,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"에러 발생: {str(e)}")
        return None


def chat_interface():
    """
    사용자와 대화형 인터페이스를 제공하는 함수
    """
    print("한국외국어대학교 컴퓨터공학과 챗봇에 오신 것을 환영합니다!")
    print("종료하려면 'quit', 'exit', '종료' 중 하나를 입력하세요.")
    print("-" * 50)

    while True:
        user_input = input("\n질문을 입력하세요: ")

        if user_input.lower() in ["quit", "exit", "종료"]:
            print("챗봇을 종료합니다. 감사합니다!")
            break

        if not user_input.strip():
            print("질문을 입력해주세요.")
            continue

        response = call_gpt(user_input)
        if response:
            print("\n답변:", response)
        else:
            print("죄송합니다. 응답을 생성하는 중에 오류가 발생했습니다.")


if __name__ == "__main__":
    chat_interface()
