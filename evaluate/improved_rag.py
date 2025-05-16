"""
개선된 RAG 시스템 모듈

이 모듈은 Reranker를 적용한 개선된 RAG 시스템을 구현합니다.
"""

from typing import List, Dict, Any
import json
import os
import sys
import logging

# 프로젝트 루트를 추가하여 app 모듈에 접근할 수 있도록 합니다
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from app.services.embeddings import find_similar_chunks
from app.services.rag import format_context_from_chunks, load_prompts
from app.core.config import settings
from app.core.utils import get_openai_client
from evaluate.reranker import rerank_documents

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def improved_generate_rag_response(
    query: str, system_key: str = "rag", use_reranker: bool = True
) -> str:
    """
    개선된 RAG 파이프라인을 사용하여 응답을 생성합니다.

    Args:
        query (str): 사용자 질의
        system_key (str): 사용할 시스템 프롬프트 키
        use_reranker (bool): Reranker 사용 여부

    Returns:
        str: 생성된 응답
    """
    try:
        # 1. 초기 문서 검색 (더 많은 문서를 검색)
        initial_chunk_count = 10 if use_reranker else 3
        initial_chunks = find_similar_chunks(query, top_k=initial_chunk_count)

        if not initial_chunks:
            return "죄송합니다. 질문에 관련된 정보를 찾을 수 없습니다."

        # 2. 재정렬기(reranker)를 사용하여 문서 재정렬 (선택적)
        if use_reranker and len(initial_chunks) > 1:
            logger.info("Reranker를 적용하여 문서를 재정렬합니다...")
            chunks_for_context = rerank_documents(query, initial_chunks, top_n=3)
        else:
            chunks_for_context = initial_chunks[:3]  # 기존 방식으로 상위 3개 선택

        # 3. 검색된 청크로부터 컨텍스트 구성
        context = format_context_from_chunks(chunks_for_context)

        # 4. 프롬프트 로드
        prompts = load_prompts()

        # 5. LLM으로 응답 생성
        client = get_openai_client()
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": prompts["system_prompts"][system_key]},
                {"role": "user", "content": f"컨텍스트: {context}\n\n질문: {query}"},
            ],
            temperature=0.3,
            max_tokens=1000,
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"응답 생성 중 오류 발생: {str(e)}")
        return f"죄송합니다. 응답을 생성하는 중에 오류가 발생했습니다: {str(e)}"


def compare_rag_responses(query: str) -> Dict[str, Any]:
    """
    기존 RAG와 개선된 RAG의 응답을 비교합니다.

    Args:
        query (str): 사용자 질의

    Returns:
        Dict[str, Any]: 비교 결과
    """
    # 기존 RAG 응답 생성
    logger.info("기존 RAG 시스템으로 응답 생성 중...")
    standard_response = improved_generate_rag_response(query, use_reranker=False)

    # 개선된 RAG 응답 생성
    logger.info("개선된 RAG 시스템(Reranker 적용)으로 응답 생성 중...")
    improved_response = improved_generate_rag_response(query, use_reranker=True)

    import datetime

    # 응답 비교 결과
    comparison_result = {
        "query": query,
        "standard_response": standard_response,
        "improved_response": improved_response,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    return comparison_result


def save_comparison_results(
    results: Dict[str, Any],
    output_file: str = "evaluate/evaluation_results/rag_comparison.json",
):
    """
    RAG 응답 비교 결과를 JSON 파일로 저장합니다.

    Args:
        results (Dict[str, Any]): 비교 결과
        output_file (str): 출력 파일 경로
    """
    # 디렉토리가 없으면 생성
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # 기존 파일이 있으면 내용 로드
    existing_results = []
    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                existing_results = json.load(f)
                if not isinstance(existing_results, list):
                    existing_results = [existing_results]
        except Exception:
            existing_results = []

    # 새 결과 추가
    existing_results.append(results)

    # 결과 저장
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(existing_results, f, ensure_ascii=False, indent=2)

    logger.info(f"RAG 비교 결과가 {output_file}에 저장되었습니다.")


if __name__ == "__main__":
    # 예시 질의로 RAG 시스템 비교
    sample_query = "컴퓨터공학과 졸업요건은 어떻게 되나요?"
    print(f"샘플 질의: {sample_query}")

    comparison_result = compare_rag_responses(sample_query)

    # 결과 출력
    print("\n=== 기존 RAG 응답 ===")
    print(comparison_result["standard_response"])

    print("\n=== 개선된 RAG 응답 (Reranker 적용) ===")
    print(comparison_result["improved_response"])

    # 결과 저장
    save_comparison_results(comparison_result)
