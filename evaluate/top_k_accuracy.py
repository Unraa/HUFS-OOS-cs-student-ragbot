"""
Top-k 문서 정확도를 평가하는 모듈

이 모듈은 RAG 시스템이 검색한 문서의 Top-k 정확도를 평가하는 함수를 제공합니다.
"""

import json
import os
import sys
from typing import Any, Dict, List

# 프로젝트 루트를 추가하여 app 모듈에 접근할 수 있도록 합니다
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from app.services.embeddings import find_similar_chunks


def evaluate_top_k_accuracy(
    test_queries: List[str],
    ground_truth_docs: List[List[str]],
    k_values: List[int] = [1, 3, 5, 10],
) -> Dict[str, Any]:
    """
    Top-k 문서 정확도를 평가합니다.

    Args:
        test_queries (List[str]): 테스트 질의 목록
        ground_truth_docs (List[List[str]]): 각 질의에 대한 정답 문서 ID 목록
        k_values (List[int]): 평가할 k 값 목록 (기본값: [1, 3, 5, 10])

    Returns:
        Dict: 정확도 지표를 포함한 결과 딕셔너리
    """
    total_queries = len(test_queries)
    results = {}

    # 각 k 값에 대해 정확도 계산
    for k in k_values:
        hit_count = 0
        query_results = []

        for i, query in enumerate(test_queries):
            # 문서 검색
            retrieved_docs = find_similar_chunks(query, top_k=k)
            retrieved_ids = [doc["id"] for doc in retrieved_docs]

            # 정답 문서가 검색된 문서에 포함되어 있는지 확인
            hit = any(doc_id in retrieved_ids for doc_id in ground_truth_docs[i])
            hit_count += 1 if hit else 0

            # 개별 질의 결과 저장
            query_results.append(
                {
                    "query": query,
                    "ground_truth_docs": ground_truth_docs[i],
                    "retrieved_docs": retrieved_ids,
                    "hit": hit,
                }
            )

        # 해당 k 값에 대한 정확도
        accuracy = hit_count / total_queries if total_queries > 0 else 0

        results[f"top_{k}"] = {
            "accuracy": accuracy,
            "hits": hit_count,
            "total": total_queries,
            "query_results": query_results,
        }

    return results


def save_accuracy_results(
    results: Dict[str, Any],
    output_file: str = "evaluate/evaluation_results/top_k_accuracy.json",
):
    """
    정확도 평가 결과를 JSON 파일로 저장합니다.

    Args:
        results (Dict[str, Any]): 정확도 평가 결과
        output_file (str): 출력 파일 경로
    """
    # 디렉토리가 없으면 생성
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"정확도 평가 결과가 {output_file}에 저장되었습니다.")


if __name__ == "__main__":
    # 테스트 데이터셋 로드 예시
    try:
        with open("evaluate/test_dataset.json", "r", encoding="utf-8") as f:
            test_data = json.load(f)

        accuracy_results = evaluate_top_k_accuracy(
            test_data["queries"], test_data["ground_truth_doc_ids"]
        )

        # 결과 출력
        for k, result in accuracy_results.items():
            print(
                f"{k} 정확도: {result['accuracy']:.2f} ({result['hits']}/{result['total']})"
            )

        # 결과 저장
        save_accuracy_results(accuracy_results)

    except FileNotFoundError:
        print(
            "테스트 데이터셋 파일을 찾을 수 없습니다. 'evaluate/test_dataset.json' 파일을 생성해주세요."
        )
    except Exception as e:
        print(f"평가 중 오류 발생: {str(e)}")
