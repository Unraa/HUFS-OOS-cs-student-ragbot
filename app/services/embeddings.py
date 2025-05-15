import os
from typing import List, Dict
import numpy as np
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from app.core.utils import get_openai_client
from app.core.config import settings
from app.services.markdown_processor import process_markdown_documents


def get_chroma_client():
    """
    ChromaDB 클라이언트를 초기화하고 반환합니다.

    Returns:
        chromadb.PersistentClient: 초기화된 ChromaDB 클라이언트
    """
    # 디렉토리가 없으면 생성
    os.makedirs(settings.CHROMA_DB_DIR, exist_ok=True)

    # 클라이언트 생성
    return chromadb.PersistentClient(path=settings.CHROMA_DB_DIR)


def get_or_create_collection():
    """
    ChromaDB 컬렉션을 가져오거나 생성합니다.

    Returns:
        chromadb.Collection: ChromaDB 컬렉션
    """
    client = get_chroma_client()

    # OpenAI 임베딩 함수 설정
    embedding_function = OpenAIEmbeddingFunction(
        api_key=settings.OPENAI_API_KEY, model_name=settings.EMBEDDING_MODEL
    )

    # 컬렉션 생성 또는 가져오기
    return client.get_or_create_collection(
        name=settings.CHROMA_COLLECTION_NAME,
        embedding_function=embedding_function,
        metadata={"hnsw:space": "cosine"},  # FAISS HNSW 인덱스 사용
    )


def generate_embedding(text: str) -> List[float]:
    """
    OpenAI API를 사용하여 텍스트에 대한 임베딩 벡터를 생성합니다.

    Args:
        text (str): 임베딩할 텍스트

    Returns:
        List[float]: 임베딩 벡터
    """
    try:
        client = get_openai_client()
        response = client.embeddings.create(model=settings.EMBEDDING_MODEL, input=text)
        # 응답에서 임베딩 벡터 추출
        embedding = response.data[0].embedding
        return embedding
    except Exception as e:
        print(f"임베딩 생성 중 오류 발생: {str(e)}")
        return []


def find_similar_chunks(query: str, top_k: int = 3) -> List[Dict]:
    """
    사용자 쿼리에 가장 유사한 청크를 ChromaDB에서 검색합니다.

    Args:
        query (str): 사용자 쿼리
        top_k (int, optional): 반환할 최상위 유사 청크 수. 기본값은 3.

    Returns:
        List[Dict]: 상위 k개의 유사한 청크 목록
    """
    try:
        collection = get_or_create_collection()

        # 컬렉션이 비어있는 경우
        if collection.count() == 0:
            print("ChromaDB가 비어있습니다. 데이터를 추가해주세요.")
            return []

        # ChromaDB에서 검색
        results = collection.query(query_texts=[query], n_results=top_k)

        # 결과 포맷 변환
        chunks = []
        for i in range(len(results["ids"][0])):
            chunk = {
                "id": results["ids"][0][i],
                "title": results["metadatas"][0][i].get("title", "제목 없음"),
                "content": results["documents"][0][i],
                "source": results["metadatas"][0][i].get("source", "출처 미상"),
            }
            chunks.append(chunk)

        return chunks

    except Exception as e:
        print(f"ChromaDB 검색 중 오류 발생: {str(e)}")
        return []


def generate_embeddings_for_chunks(chunks: List[Dict[str, str]]) -> List[Dict]:
    """
    청크 목록에 대한 임베딩을 생성하고 ChromaDB에 저장합니다.

    Args:
        chunks (List[Dict[str, str]]): 청킹된, 각각 'title'과 'content'를 포함하는 딕셔너리 목록

    Returns:
        List[Dict]: 저장된 청크 목록
    """
    # ChromaDB 컬렉션 가져오기
    collection = get_or_create_collection()

    # 기존 데이터 모두 제거 (새로 생성)
    try:
        # 기존 모든 문서의 ID를 가져옵니다
        if collection.count() > 0:
            all_ids = collection.get()["ids"]
            # 모든 ID를 사용하여 데이터 삭제
            if all_ids:
                collection.delete(ids=all_ids)
            print(f"{len(all_ids)}개의 기존 문서가 삭제되었습니다.")
    except Exception as e:
        print(f"기존 데이터 삭제 중 오류 발생: {str(e)}")
        # 오류가 발생해도 계속 진행

    ids = []
    documents = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        print(f"청크 {i+1}/{len(chunks)}에 대한 임베딩 생성 및 저장 중...")

        # 청크 데이터 준비
        chunk_id = f"chunk_{i}"
        text = chunk["content"]
        metadata = {"title": chunk["title"], "source": chunk.get("source", "출처 미상")}

        # ChromaDB에 추가하기 위한 데이터 수집
        ids.append(chunk_id)
        documents.append(text)
        metadatas.append(metadata)

    # 배치로 ChromaDB에 데이터 추가
    collection.add(ids=ids, documents=documents, metadatas=metadatas)

    print(f"ChromaDB에 {len(chunks)} 청크 저장 완료")

    return chunks
