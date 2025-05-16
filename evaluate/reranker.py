"""
Reranker 모듈

이 모듈은 검색된 문서를 재정렬하는 Reranker 기능을 제공합니다.
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

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def rerank_documents(
    query: str, initial_docs: List[Dict], top_n: int = 3
) -> List[Dict]:
    """
    검색된 문서를 재정렬합니다.

    Args:
        query (str): 사용자 질의
        initial_docs (List[Dict]): 초기 검색된 문서 목록
        top_n (int): 최종적으로 반환할 문서 수

    Returns:
        List[Dict]: 재정렬된 문서 목록
    """
    try:
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
    except ImportError:
        logger.error("필요한 패키지가 설치되지 않았습니다. 다음 명령어로 설치해주세요:")
        logger.error("pip install torch transformers")
        return initial_docs[:top_n]  # 패키지가 없으면 기존 순서로 반환

    # 문서가 없거나 하나뿐인 경우 그대로 반환
    if not initial_docs or len(initial_docs) <= 1:
        return initial_docs

    try:
        # 재정렬 모델 로드
        logger.info("재정렬 모델을 로드합니다...")
        model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"  # 또는 다른 적합한 모델
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)

        # 점수 계산을 위한 데이터 준비
        pairs = []
        for doc in initial_docs:
            pairs.append([query, doc["content"]])

        logger.info(f"{len(pairs)}개 문서에 대한 재정렬을 시작합니다...")

        # 모델 입력 준비
        features = tokenizer.batch_encode_plus(
            pairs,
            max_length=512,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        # 점수 계산
        with torch.no_grad():
            scores = model(**features).logits.squeeze(-1).numpy()

        # 점수와 문서를 묶어서 정렬
        doc_scores = [(doc, score) for doc, score in zip(initial_docs, scores)]
        ranked_docs = sorted(doc_scores, key=lambda x: x[1], reverse=True)

        # 상위 N개 문서 반환
        result_docs = [doc for doc, _ in ranked_docs[:top_n]]
        logger.info(f"재정렬 완료: {len(initial_docs)}개 문서 중 상위 {top_n}개 선택")

        return result_docs

    except Exception as e:
        logger.error(f"재정렬 중 오류 발생: {str(e)}")
        # 오류 발생 시 원래 순서대로 반환
        return initial_docs[:top_n]


def improved_search_with_reranker(
    query: str, initial_k: int = 10, final_k: int = 3
) -> List[Dict]:
    """
    Reranker를 적용한 개선된 문서 검색 함수

    Args:
        query (str): 사용자 질의
        initial_k (int): 초기 검색에서 가져올 문서 수
        final_k (int): 재정렬 후 최종적으로 반환할 문서 수

    Returns:
        List[Dict]: 최종 선택된 문서 목록
    """
    # 1. 초기 문서 검색 (더 많은 문서를 검색)
    initial_chunks = find_similar_chunks(query, top_k=initial_k)

    if not initial_chunks:
        return []

    # 2. 재정렬기(reranker)를 사용하여 문서 재정렬
    reranked_chunks = rerank_documents(query, initial_chunks, top_n=final_k)

    return reranked_chunks


def evaluate_reranker_improvement(
    test_queries: List[str], ground_truth_docs: List[List[str]]
) -> Dict[str, Any]:
    """
    Reranker의 성능 향상을 평가합니다.

    Args:
        test_queries (List[str]): 테스트 질의 목록
        ground_truth_docs (List[List[str]]): 각 질의에 대한 정답 문서 ID 목록

    Returns:
        Dict[str, Any]: 평가 결과
    """
    results = {"queries": [], "standard_hits": 0, "reranked_hits": 0, "improvements": 0}

    for i, query in enumerate(test_queries):
        logger.info(f"질의 {i+1}/{len(test_queries)} 평가 중...")

        # 기존 검색 방식
        standard_docs = find_similar_chunks(query, top_k=3)
        standard_ids = [doc["id"] for doc in standard_docs]
        standard_hit = any(doc_id in standard_ids for doc_id in ground_truth_docs[i])

        # Reranker 적용 (초기 10개 검색 후 상위 3개 선택)
        reranked_docs = improved_search_with_reranker(query, initial_k=10, final_k=3)
        reranked_ids = [doc["id"] for doc in reranked_docs]
        reranked_hit = any(doc_id in reranked_ids for doc_id in ground_truth_docs[i])

        # 개선 여부 확인
        improved = not standard_hit and reranked_hit

        # 결과 업데이트
        results["standard_hits"] += 1 if standard_hit else 0
        results["reranked_hits"] += 1 if reranked_hit else 0
        results["improvements"] += 1 if improved else 0

        # 개별 질의 결과 저장
        results["queries"].append(
            {
                "query": query,
                "ground_truth_docs": ground_truth_docs[i],
                "standard_docs": standard_ids,
                "reranked_docs": reranked_ids,
                "standard_hit": standard_hit,
                "reranked_hit": reranked_hit,
                "improved": improved,
            }
        )

    # 전체 통계 계산
    total_queries = len(test_queries)
    results["total_queries"] = total_queries
    results["standard_accuracy"] = (
        results["standard_hits"] / total_queries if total_queries > 0 else 0
    )
    results["reranked_accuracy"] = (
        results["reranked_hits"] / total_queries if total_queries > 0 else 0
    )
    results["improvement_rate"] = (
        results["improvements"] / total_queries if total_queries > 0 else 0
    )

    return results


def save_reranker_results(
    results: Dict[str, Any],
    output_file: str = "evaluate/evaluation_results/reranker_improvement.json",
):
    """
    Reranker 평가 결과를 JSON 파일로 저장합니다.

    Args:
        results (Dict[str, Any]): Reranker 평가 결과
        output_file (str): 출력 파일 경로
    """
    # 디렉토리가 없으면 생성
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    logger.info(f"Reranker 평가 결과가 {output_file}에 저장되었습니다.")


if __name__ == "__main__":
    # 테스트 데이터셋 로드 예시
    try:
        with open("evaluate/test_dataset.json", "r", encoding="utf-8") as f:
            test_data = json.load(f)

        reranker_results = evaluate_reranker_improvement(
            test_data["queries"], test_data["ground_truth_doc_ids"]
        )

        # 결과 출력
        print("\nReranker 성능 평가 결과:")
        print(
            f"기존 정확도: {reranker_results['standard_accuracy']:.4f} ({reranker_results['standard_hits']}/{reranker_results['total_queries']})"
        )
        print(
            f"재정렬 후 정확도: {reranker_results['reranked_accuracy']:.4f} ({reranker_results['reranked_hits']}/{reranker_results['total_queries']})"
        )
        print(
            f"개선 비율: {reranker_results['improvement_rate']:.4f} ({reranker_results['improvements']}/{reranker_results['total_queries']})"
        )

        # 결과 저장
        save_reranker_results(reranker_results)

    except FileNotFoundError:
        logger.error(
            "테스트 데이터셋 파일을 찾을 수 없습니다. 'evaluate/test_dataset.json' 파일을 생성해주세요."
        )
    except Exception as e:
        logger.error(f"평가 중 오류 발생: {str(e)}")
