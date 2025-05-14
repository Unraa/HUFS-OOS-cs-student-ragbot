import os
from typing import List, Dict
import numpy as np
import json
from dotenv import load_dotenv
from openai import OpenAI
from markdown_processor import process_markdown_documents

# .env 파일에서 환경 변수 로드
load_dotenv()

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_embedding(text: str) -> List[float]:
    """
    OpenAI API를 사용하여 텍스트에 대한 임베딩 벡터를 생성합니다.

    Args:
        text (str): 임베딩할 텍스트

    Returns:
        List[float]: 임베딩 벡터
    """
    try:
        response = client.embeddings.create(model="text-embedding-3-small", input=text)
        # 응답에서 임베딩 벡터 추출
        embedding = response.data[0].embedding
        return embedding
    except Exception as e:
        print(f"임베딩 생성 중 오류 발생: {str(e)}")
        return []


def generate_embeddings_for_chunks(chunks: List[Dict[str, str]]) -> List[Dict]:
    """
    청크 목록에 대한 임베딩을 생성하고 각 청크에 임베딩을 추가합니다.

    Args:
        chunks (List[Dict[str, str]]): 청킹된, 각각 'title'과 'content'를 포함하는 딕셔너리 목록

    Returns:
        List[Dict]: 각 청크에 'embedding' 필드가 추가된, 업데이트된 딕셔너리 목록
    """
    chunks_with_embeddings = []

    for i, chunk in enumerate(chunks):
        print(f"청크 {i+1}/{len(chunks)}에 대한 임베딩 생성 중...")

        # 임베딩을 위한 텍스트 준비 (제목 + 내용)
        text_for_embedding = f"{chunk['title']}\n\n{chunk['content']}"

        # 임베딩 생성
        embedding = generate_embedding(text_for_embedding)

        # 임베딩을 포함한 새 딕셔너리 생성
        chunk_with_embedding = {**chunk, "embedding": embedding}  # 기존 청크 정보 복사

        chunks_with_embeddings.append(chunk_with_embedding)

    return chunks_with_embeddings


def save_vector_store(
    chunks_with_embeddings: List[Dict], output_file: str = "vector_store.json"
):
    """
    임베딩이 포함된 청크들을 JSON 파일로 저장합니다.

    Args:
        chunks_with_embeddings (List[Dict]): 임베딩이 포함된 청크 목록
        output_file (str, optional): 저장할 파일 경로. 기본값은 'vector_store.json'.
    """
    # JSON으로 저장하기 위해 NumPy 배열을 리스트로 변환
    serializable_chunks = []

    for chunk in chunks_with_embeddings:
        serializable_chunk = {
            "title": chunk["title"],
            "content": chunk["content"],
            "source": chunk["source"],
            "embedding": chunk["embedding"],  # 이미 리스트 형태로 반환됨
        }
        serializable_chunks.append(serializable_chunk)

    # JSON 파일로 저장
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(serializable_chunks, f, ensure_ascii=False, indent=2)

    print(f"벡터 저장소가 {output_file}에 저장되었습니다.")


def load_vector_store(input_file: str = "vector_store.json") -> List[Dict]:
    """
    저장된 벡터 저장소를 로드합니다.

    Args:
        input_file (str, optional): 로드할 파일 경로. 기본값은 'vector_store.json'.

    Returns:
        List[Dict]: 로드된 청크 목록
    """
    if not os.path.exists(input_file):
        print(f"파일이 존재하지 않습니다: {input_file}")
        return []

    with open(input_file, "r", encoding="utf-8") as f:
        vector_store = json.load(f)

    print(f"벡터 저장소 로드 완료: {len(vector_store)} 청크")
    return vector_store


if __name__ == "__main__":
    # 1. 마크다운 문서 처리 및 청킹
    directory_path = "study_docs"
    _, chunks = process_markdown_documents(directory_path)

    # 2. 임베딩 생성
    chunks_with_embeddings = generate_embeddings_for_chunks(chunks)

    # 3. 벡터 저장소 저장
    save_vector_store(chunks_with_embeddings)

    # 4. 저장된 벡터 저장소 로드 (테스트)
    loaded_chunks = load_vector_store()
    print(f"로드된 벡터 저장소: {len(loaded_chunks)} 청크")
