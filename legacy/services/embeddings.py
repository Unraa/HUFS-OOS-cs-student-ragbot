import json
import os
from typing import Dict, List

import chromadb
import numpy as np
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from app.core.config import settings
from app.core.utils import get_openai_client
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
    query: str, vector_store: List[Dict] = None, top_k: int = 3
) -> List[Dict]:
    """
    사용자 쿼리에 가장 유사한 청크를 찾습니다.

    이 함수는 ChromaDB를 통해 검색하거나, 기존 vector_store를 사용하여 호환성을 유지합니다.

    Args:
        query (str): 사용자 쿼리
        vector_store (List[Dict], optional): 벡터 저장소 (호환성 위해 유지)
        top_k (int, optional): 반환할 최상위 유사 청크 수. 기본값은 3.

    Returns:
        List[Dict]: 상위 k개의 유사한 청크 목록
    """
    # ChromaDB 사용
    try:
        collection = get_or_create_collection()

        # 컬렉션이 비어있으면 기존 vector_store 사용
        if collection.count() == 0 and vector_store is not None:
            print("ChromaDB가 비어있어 기존 벡터 저장소를 사용합니다.")
            return find_similar_chunks_legacy(query, vector_store, top_k)

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
        # 오류 발생 시 기존 벡터 저장소 사용 시도
        if vector_store is not None:
            print("기존 벡터 저장소를 사용하여 검색합니다.")
            return find_similar_chunks_legacy(query, vector_store, top_k)
        return []


def find_similar_chunks_legacy(
    query: str, vector_store: List[Dict], top_k: int = 3
) -> List[Dict]:
    """
    기존 방식을 사용하여 사용자 쿼리에 가장 유사한 청크를 찾습니다. (호환성 유지)

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


def generate_embeddings_for_chunks(chunks: List[Dict[str, str]]) -> List[Dict]:
    """
    청크 목록에 대한 임베딩을 생성하고 ChromaDB에 저장합니다.

    Args:
        chunks (List[Dict[str, str]]): 청킹된, 각각 'title'과 'content'를 포함하는 딕셔너리 목록

    Returns:
        List[Dict]: 각 청크에 'embedding' 필드가 추가된, 업데이트된 딕셔너리 목록
        (호환성을 위해 이전 형식도 반환)
    """
    # ChromaDB 컬렉션 가져오기
    collection = get_or_create_collection()

    # 기존 데이터 모두 제거 (새로 생성)
    collection.delete(where={})

    ids = []
    documents = []
    metadatas = []
    chunks_with_embeddings = []

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

        # 호환성을 위해 임베딩도 별도로 생성
        text_for_embedding = f"{chunk['title']}\n\n{chunk['content']}"
        embedding = generate_embedding(text_for_embedding)
        chunk_with_embedding = {**chunk, "embedding": embedding}
        chunks_with_embeddings.append(chunk_with_embedding)

    # 배치로 ChromaDB에 데이터 추가
    collection.add(ids=ids, documents=documents, metadatas=metadatas)

    print(f"ChromaDB에 {len(chunks)} 청크 저장 완료")

    # 호환성을 위해 기존 형식 데이터도 저장
    save_vector_store(chunks_with_embeddings)

    return chunks_with_embeddings


def save_vector_store(chunks_with_embeddings: List[Dict], output_file: str = None):
    """
    임베딩이 포함된 청크들을 JSON 파일로 저장합니다. (호환성 유지)

    Args:
        chunks_with_embeddings (List[Dict]): 임베딩이 포함된 청크 목록
        output_file (str, optional): 저장할 파일 경로. 기본값은 설정 파일의 경로.
    """
    if output_file is None:
        output_file = settings.VECTOR_STORE_PATH

    # 출력 디렉토리가 없으면 생성
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # JSON으로 저장하기 위해 NumPy 배열을 리스트로 변환
    serializable_chunks = []

    for chunk in chunks_with_embeddings:
        serializable_chunk = {
            "title": chunk["title"],
            "content": chunk["content"],
            "source": chunk.get("source", "출처 미상"),
            "embedding": chunk["embedding"],  # 이미 리스트 형태로 반환됨
        }
        serializable_chunks.append(serializable_chunk)

    # JSON 파일로 저장
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(serializable_chunks, f, ensure_ascii=False, indent=2)

    print(f"벡터 저장소가 {output_file}에 저장되었습니다.")


def load_vector_store(input_file: str = None) -> List[Dict]:
    """
    벡터 저장소를 로드합니다. ChromaDB에서 로드하고, 실패 시 기존 JSON 파일을 사용합니다.

    Args:
        input_file (str, optional): 로드할 파일 경로. 기본값은 설정 파일의 경로.

    Returns:
        List[Dict]: 로드된 청크 목록
    """
    try:
        # ChromaDB 컬렉션 확인
        collection = get_or_create_collection()

        # ChromaDB에 데이터가 있으면 빈 리스트 반환 (ChromaDB가 직접 검색에 사용됨)
        if collection.count() > 0:
            print(f"ChromaDB에서 {collection.count()} 청크 로드 완료")
            return []  # ChromaDB를 사용할 때는 빈 리스트 반환

    except Exception as e:
        print(f"ChromaDB 로드 중 오류 발생: {str(e)}")

    # 실패하거나 컬렉션이 비어있으면 기존 JSON 파일 사용
    if input_file is None:
        input_file = settings.VECTOR_STORE_PATH

    if not os.path.exists(input_file):
        print(f"파일이 존재하지 않습니다: {input_file}")
        return []

    with open(input_file, "r", encoding="utf-8") as f:
        vector_store = json.load(f)

    print(f"JSON 벡터 저장소 로드 완료: {len(vector_store)} 청크")

    # JSON 데이터를 ChromaDB로 마이그레이션 시도
    try:
        migrate_json_to_chromadb(vector_store)
    except Exception as e:
        print(f"JSON 데이터 마이그레이션 중 오류 발생: {str(e)}")

    return vector_store


def migrate_json_to_chromadb(vector_store: List[Dict]):
    """
    JSON 벡터 저장소에서 ChromaDB로 데이터를 마이그레이션합니다.

    Args:
        vector_store (List[Dict]): JSON 형식의 벡터 저장소
    """
    # 이미 ChromaDB가 데이터를 포함하고 있는지 확인
    collection = get_or_create_collection()

    if collection.count() > 0:
        print("ChromaDB가 이미 데이터를 포함하고 있어 마이그레이션을 건너뜁니다.")
        return

    print(f"JSON 데이터 {len(vector_store)}개 청크를 ChromaDB로 마이그레이션합니다...")

    # 배치 크기 설정
    batch_size = 100

    for i in range(0, len(vector_store), batch_size):
        batch = vector_store[i : i + batch_size]

        ids = [f"chunk_{i+j}" for j in range(len(batch))]
        documents = [item["content"] for item in batch]
        metadatas = [
            {"title": item["title"], "source": item.get("source", "출처 미상")}
            for item in batch
        ]

        # 컬렉션에 배치 추가
        collection.add(ids=ids, documents=documents, metadatas=metadatas)

    print(f"ChromaDB 마이그레이션 완료: {len(vector_store)} 청크")
