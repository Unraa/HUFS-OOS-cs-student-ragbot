import os
import numpy as np
from typing import List, Dict, Tuple
from dotenv import load_dotenv
from openai import OpenAI
import yaml
from embeddings_generator import load_vector_store, generate_embedding

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


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    두 벡터 간의 코사인 유사도를 계산합니다.

    Args:
        vec1 (List[float]): 첫 번째 벡터
        vec2 (List[float]): 두 번째 벡터

    Returns:
        float: 코사인 유사도 (-1에서 1 사이의 값)
    """
    # NumPy 배열로 변환
    np_vec1 = np.array(vec1)
    np_vec2 = np.array(vec2)

    # 코사인 유사도 계산
    return np.dot(np_vec1, np_vec2) / (
        np.linalg.norm(np_vec1) * np.linalg.norm(np_vec2)
    )


def find_similar_chunks(
    query: str, vector_store: List[Dict], top_k: int = 3
) -> List[Dict]:
    """
    사용자 쿼리에 가장 유사한 청크를 찾습니다.

    Args:
        query (str): 사용자 쿼리
        vector_store (List[Dict]): 벡터 저장소
        top_k (int, optional): 반환할 최상위 유사 청크 수. 기본값은 3.

    Returns:
        List[Dict]: 상위 k개의 유사한 청크 목록
    """
    # 쿼리에 대한 임베딩 생성
    query_embedding = generate_embedding(query)

    # 각 청크와의 유사도 계산
    chunk_similarities = []
    for chunk in vector_store:
        chunk_embedding = chunk["embedding"]
        similarity = cosine_similarity(query_embedding, chunk_embedding)
        chunk_similarities.append((chunk, similarity))

    # 유사도에 따라 내림차순 정렬
    sorted_chunks = sorted(chunk_similarities, key=lambda x: x[1], reverse=True)

    # 상위 k개 청크 반환
    top_chunks = [chunk for chunk, _ in sorted_chunks[:top_k]]

    return top_chunks


def format_context_from_chunks(chunks: List[Dict]) -> str:
    """
    검색된 청크들로부터 LLM에 제공할 컨텍스트를 포맷팅합니다.

    Args:
        chunks (List[Dict]): 유사한 청크들의 목록

    Returns:
        str: 포맷팅된 컨텍스트 문자열
    """
    formatted_context = (
        "다음은 한국외국어대학교 컴퓨터공학과 관련 문서에서 검색된 내용입니다:\n\n"
    )

    for i, chunk in enumerate(chunks, 1):
        formatted_context += f"--- 문서 {i}: {chunk['title']} ---\n"
        formatted_context += chunk["content"]
        formatted_context += "\n\n"

    return formatted_context


def generate_rag_response(
    query: str, vector_store: List[Dict], system_key: str = "rag"
) -> str:
    """
    RAG 접근 방식을 사용하여 사용자 쿼리에 응답을 생성합니다.

    Args:
        query (str): 사용자 쿼리
        vector_store (List[Dict]): 벡터 저장소
        system_key (str, optional): 시스템 프롬프트 키. 기본값은 "rag".

    Returns:
        str: 생성된 응답
    """
    try:
        # 1. 관련 청크 검색
        similar_chunks = find_similar_chunks(query, vector_store)

        # 검색 결과가 없는 경우
        if not similar_chunks:
            return "죄송합니다. 질문에 관련된 정보를 찾을 수 없습니다."

        # 2. 검색된 청크로부터 컨텍스트 구성
        context = format_context_from_chunks(similar_chunks)

        # 3. 프롬프트 로드
        prompts = load_prompts()

        # 4. LLM으로 응답 생성
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompts["system_prompts"][system_key]},
                {"role": "user", "content": f"컨텍스트: {context}\n\n질문: {query}"},
            ],
            temperature=0.3,
            max_tokens=1000,
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"응답 생성 중 오류 발생: {str(e)}")
        return "죄송합니다. 응답을 생성하는 중에 오류가 발생했습니다."


def chat_interface():
    """
    사용자와 대화형 인터페이스를 제공하는 함수
    """
    print("한국외국어대학교 컴퓨터공학과 RAG 챗봇에 오신 것을 환영합니다!")
    print("종료하려면 'quit', 'exit', '종료' 중 하나를 입력하세요.")
    print("-" * 50)

    # 벡터 저장소 로드
    vector_store = load_vector_store()
    if not vector_store:
        print("벡터 저장소를 로드할 수 없습니다. 프로그램을 종료합니다.")
        return

    print(f"성공적으로 {len(vector_store)}개의 청크가 로드되었습니다.")

    while True:
        user_input = input("\n질문을 입력하세요: ")

        if user_input.lower() in ["quit", "exit", "종료"]:
            print("챗봇을 종료합니다. 감사합니다!")
            break

        if not user_input.strip():
            print("질문을 입력해주세요.")
            continue

        print("처리 중...")
        response = generate_rag_response(user_input, vector_store)
        print("\n답변:", response)


if __name__ == "__main__":
    chat_interface()
