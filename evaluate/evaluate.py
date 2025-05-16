"""
RAG 시스템 종합 평가 모듈

이 모듈은 RAG 시스템의 종합적인 성능 평가를 수행합니다.
"""

import json
import os
import sys
import time
import logging
import argparse
from typing import Dict, Any, List, Optional

# 프로젝트 루트를 추가하여 app 모듈에 접근할 수 있도록 합니다
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# 평가 모듈 임포트
from evaluate.top_k_accuracy import evaluate_top_k_accuracy, save_accuracy_results
from evaluate.response_quality import (
    evaluate_gpt_response_quality,
    save_quality_results,
)
from evaluate.reranker import evaluate_reranker_improvement, save_reranker_results
from evaluate.test_dataset import create_test_dataset, save_test_dataset
from evaluate.improved_rag import compare_rag_responses, save_comparison_results

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def ensure_test_dataset(
    test_dataset_path: str = "evaluate/test_dataset.json",
) -> Dict[str, Any]:
    """
    테스트 데이터셋이 존재하는지 확인하고, 없으면 생성합니다.

    Args:
        test_dataset_path (str): 테스트 데이터셋 파일 경로

    Returns:
        Dict[str, Any]: 테스트 데이터셋
    """
    if not os.path.exists(test_dataset_path):
        logger.info(
            f"테스트 데이터셋이 없습니다. 새 데이터셋을 생성합니다: {test_dataset_path}"
        )
        save_test_dataset(test_dataset_path)

    with open(test_dataset_path, "r", encoding="utf-8") as f:
        test_data = json.load(f)

    return test_data


def evaluate_rag_system(
    test_dataset_path: str = "evaluate/test_dataset.json",
    output_dir: str = "evaluate/evaluation_results",
    run_all: bool = True,
    run_top_k: bool = False,
    run_response_quality: bool = False,
    run_reranker: bool = False,
    run_comparison: bool = False,
    sample_query: Optional[str] = None,
) -> Dict[str, Any]:
    """
    RAG 시스템의 전체 성능을 평가합니다.

    Args:
        test_dataset_path (str): 테스트 데이터셋 파일 경로
        output_dir (str): 평가 결과를 저장할 디렉토리
        run_all (bool): 모든 평가를 실행할지 여부
        run_top_k (bool): Top-k 정확도 평가 실행 여부
        run_response_quality (bool): 응답 품질 평가 실행 여부
        run_reranker (bool): Reranker 성능 평가 실행 여부
        run_comparison (bool): RAG 시스템 비교 실행 여부
        sample_query (Optional[str]): 비교 평가에 사용할 샘플 질의

    Returns:
        Dict[str, Any]: 평가 결과 요약
    """
    # 평가 결과를 저장할 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)

    # 테스트 데이터셋 확인 및 로드
    test_data = ensure_test_dataset(test_dataset_path)

    # 평가 시작
    logger.info("RAG 시스템 성능 평가를 시작합니다...")
    start_time = time.time()

    results_summary = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "execution_time": 0,
        "top_k_accuracy": {},
        "response_quality": {},
        "reranker_improvement": {},
        "comparison": {},
    }

    # 1. Top-k 문서 정확도 평가
    if run_all or run_top_k:
        logger.info("\n1. Top-k 문서 정확도 평가:")
        accuracy_results = evaluate_top_k_accuracy(
            test_data["queries"], test_data["ground_truth_doc_ids"]
        )

        for k, result in accuracy_results.items():
            logger.info(
                f"{k} 정확도: {result['accuracy']:.2f} ({result['hits']}/{result['total']})"
            )

        # 결과 저장
        save_accuracy_results(
            accuracy_results, os.path.join(output_dir, "top_k_accuracy.json")
        )
        results_summary["top_k_accuracy"] = {
            k: result["accuracy"] for k, result in accuracy_results.items()
        }

    # 2. GPT 응답 품질 평가
    if run_all or run_response_quality:
        logger.info("\n2. GPT 응답 품질 평가:")
        quality_results = evaluate_gpt_response_quality(
            test_data["queries"], test_data["ground_truth_answers"]
        )

        logger.info(f"평균 ROUGE-1: {quality_results['avg_rouge_1']:.4f}")
        logger.info(f"평균 ROUGE-2: {quality_results['avg_rouge_2']:.4f}")
        logger.info(f"평균 ROUGE-L: {quality_results['avg_rouge_l']:.4f}")
        logger.info(f"평균 BLEU: {quality_results['avg_bleu']:.4f}")

        # 결과 저장
        save_quality_results(
            quality_results, os.path.join(output_dir, "response_quality.json")
        )
        results_summary["response_quality"] = {
            "rouge_1": quality_results["avg_rouge_1"],
            "rouge_2": quality_results["avg_rouge_2"],
            "rouge_l": quality_results["avg_rouge_l"],
            "bleu": quality_results["avg_bleu"],
        }

    # 3. Reranker 성능 평가
    if run_all or run_reranker:
        logger.info("\n3. Reranker 성능 평가:")
        reranker_results = evaluate_reranker_improvement(
            test_data["queries"], test_data["ground_truth_doc_ids"]
        )

        logger.info(
            f"기존 정확도: {reranker_results['standard_accuracy']:.4f} ({reranker_results['standard_hits']}/{reranker_results['total_queries']})"
        )
        logger.info(
            f"재정렬 후 정확도: {reranker_results['reranked_accuracy']:.4f} ({reranker_results['reranked_hits']}/{reranker_results['total_queries']})"
        )
        logger.info(
            f"개선 비율: {reranker_results['improvement_rate']:.4f} ({reranker_results['improvements']}/{reranker_results['total_queries']})"
        )

        # 결과 저장
        save_reranker_results(
            reranker_results, os.path.join(output_dir, "reranker_improvement.json")
        )
        results_summary["reranker_improvement"] = {
            "standard_accuracy": reranker_results["standard_accuracy"],
            "reranked_accuracy": reranker_results["reranked_accuracy"],
            "improvement_rate": reranker_results["improvement_rate"],
        }

    # 4. RAG 시스템 비교 (샘플 질의에 대한)
    if run_all or run_comparison:
        logger.info("\n4. RAG 시스템 비교 (Reranker 적용 전/후):")

        # 샘플 질의가 없으면 테스트 데이터셋의 첫 번째 질의 사용
        query = sample_query if sample_query else test_data["queries"][0]
        logger.info(f"샘플 질의: {query}")

        comparison_result = compare_rag_responses(query)

        # 결과 저장
        save_comparison_results(
            comparison_result, os.path.join(output_dir, "rag_comparison.json")
        )
        results_summary["comparison"] = {
            "query": query,
            "standard_response_length": len(comparison_result["standard_response"]),
            "improved_response_length": len(comparison_result["improved_response"]),
        }

    # 평가 완료
    execution_time = time.time() - start_time
    results_summary["execution_time"] = execution_time

    # 종합 결과 저장
    with open(
        os.path.join(output_dir, "evaluation_summary.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(results_summary, f, ensure_ascii=False, indent=2)

    logger.info(f"\n평가 완료! 실행 시간: {execution_time:.2f}초")
    logger.info(f"평가 결과는 '{output_dir}' 디렉토리에 저장되었습니다.")

    return results_summary


def parse_arguments():
    """
    명령줄 인수를 파싱합니다.

    Returns:
        argparse.Namespace: 파싱된 인수
    """
    parser = argparse.ArgumentParser(description="RAG 시스템 성능 평가")

    parser.add_argument(
        "--test-dataset",
        type=str,
        default="evaluate/test_dataset.json",
        help="테스트 데이터셋 파일 경로",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="evaluate/evaluation_results",
        help="평가 결과를 저장할 디렉토리",
    )

    # 실행할 평가 유형 선택
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--all", action="store_true", default=True, help="모든 평가 실행"
    )
    group.add_argument(
        "--selective", action="store_true", help="선택적 평가 실행 (개별 옵션 사용)"
    )

    # 개별 평가 옵션
    parser.add_argument("--top-k", action="store_true", help="Top-k 정확도 평가 실행")
    parser.add_argument("--quality", action="store_true", help="응답 품질 평가 실행")
    parser.add_argument(
        "--reranker", action="store_true", help="Reranker 성능 평가 실행"
    )
    parser.add_argument(
        "--comparison", action="store_true", help="RAG 시스템 비교 실행"
    )

    # 샘플 질의
    parser.add_argument("--query", type=str, help="비교 평가에 사용할 샘플 질의")

    return parser.parse_args()


if __name__ == "__main__":
    # 명령줄 인수 파싱
    args = parse_arguments()

    # 선택적 평가 모드인 경우 all 플래그 비활성화
    run_all = args.all and not args.selective

    # 평가 실행
    evaluate_rag_system(
        test_dataset_path=args.test_dataset,
        output_dir=args.output_dir,
        run_all=run_all,
        run_top_k=args.top_k,
        run_response_quality=args.quality,
        run_reranker=args.reranker,
        run_comparison=args.comparison,
        sample_query=args.query,
    )
