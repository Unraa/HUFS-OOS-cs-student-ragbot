"""
GPT 응답 품질을 평가하는 모듈

이 모듈은 RAG 시스템이 생성한 응답의 품질을 ROUGE, BLEU 등의 지표로 평가하는 함수를 제공합니다.
"""

import json
import os
import sys
from typing import Any, Dict, List

import numpy as np

# 프로젝트 루트를 추가하여 app 모듈에 접근할 수 있도록 합니다
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from app.services.rag import generate_rag_response


def evaluate_gpt_response_quality(
    test_queries: List[str], ground_truth_answers: List[str]
) -> Dict[str, Any]:
    """
    GPT 응답 품질을 평가합니다.

    Args:
        test_queries (List[str]): 테스트 질의 목록
        ground_truth_answers (List[str]): 각 질의에 대한 정답 응답 목록

    Returns:
        Dict: 품질 평가 지표를 포함한 결과 딕셔너리
    """
    try:
        import nltk
        from nltk.translate.bleu_score import sentence_bleu
        from rouge import Rouge

        nltk.download("punkt", quiet=True)  # NLTK 데이터 다운로드
    except ImportError:
        print("필요한 패키지가 설치되지 않았습니다. 다음 명령어로 설치해주세요:")
        print("pip install rouge-score nltk")
        return {}

    rouge = Rouge()
    results = {
        "responses": [],
        "rouge_scores": [],
        "bleu_scores": [],
        "avg_rouge_1": 0,
        "avg_rouge_2": 0,
        "avg_rouge_l": 0,
        "avg_bleu": 0,
    }

    for i, query in enumerate(test_queries):
        print(f"질의 {i+1}/{len(test_queries)} 평가 중...")

        # RAG 시스템으로 응답 생성
        response = generate_rag_response(query)

        # 응답 저장
        results["responses"].append(
            {
                "query": query,
                "ground_truth": ground_truth_answers[i],
                "generated_response": response,
            }
        )

        # ROUGE 점수 계산
        try:
            rouge_scores = rouge.get_scores(response, ground_truth_answers[i])[0]
            results["rouge_scores"].append(rouge_scores)
        except Exception as e:
            print(f"ROUGE 점수 계산 중 오류 발생: {str(e)}")
            results["rouge_scores"].append(
                {"rouge-1": {"f": 0}, "rouge-2": {"f": 0}, "rouge-l": {"f": 0}}
            )

        # BLEU 점수 계산
        try:
            # 토큰화
            reference = [ground_truth_answers[i].split()]
            candidate = response.split()

            # 짧은 응답에 대한 처리
            weights = (1.0 / min(4, len(candidate)),) * min(4, len(candidate))
            bleu_score = sentence_bleu(reference, candidate, weights=weights)
            results["bleu_scores"].append(bleu_score)
        except Exception as e:
            print(f"BLEU 점수 계산 중 오류 발생: {str(e)}")
            results["bleu_scores"].append(0)

    # 평균 점수 계산
    if results["rouge_scores"]:
        results["avg_rouge_1"] = np.mean(
            [score["rouge-1"]["f"] for score in results["rouge_scores"]]
        )
        results["avg_rouge_2"] = np.mean(
            [score["rouge-2"]["f"] for score in results["rouge_scores"]]
        )
        results["avg_rouge_l"] = np.mean(
            [score["rouge-l"]["f"] for score in results["rouge_scores"]]
        )

    if results["bleu_scores"]:
        results["avg_bleu"] = np.mean(results["bleu_scores"])

    return results


def save_quality_results(
    results: Dict[str, Any],
    output_file: str = "evaluate/evaluation_results/response_quality.json",
):
    """
    품질 평가 결과를 JSON 파일로 저장합니다.

    Args:
        results (Dict[str, Any]): 품질 평가 결과
        output_file (str): 출력 파일 경로
    """
    # 디렉토리가 없으면 생성
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # NumPy 배열을 일반 파이썬 타입으로 변환
    serializable_results = json.loads(
        json.dumps(
            results, default=lambda x: float(x) if isinstance(x, np.floating) else x
        )
    )

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(serializable_results, f, ensure_ascii=False, indent=2)

    print(f"응답 품질 평가 결과가 {output_file}에 저장되었습니다.")


if __name__ == "__main__":
    # 테스트 데이터셋 로드 예시
    try:
        with open("evaluate/test_dataset.json", "r", encoding="utf-8") as f:
            test_data = json.load(f)

        quality_results = evaluate_gpt_response_quality(
            test_data["queries"], test_data["ground_truth_answers"]
        )

        # 결과 출력
        print("\nGPT 응답 품질 평가 결과:")
        print(f"평균 ROUGE-1: {quality_results['avg_rouge_1']:.4f}")
        print(f"평균 ROUGE-2: {quality_results['avg_rouge_2']:.4f}")
        print(f"평균 ROUGE-L: {quality_results['avg_rouge_l']:.4f}")
        print(f"평균 BLEU: {quality_results['avg_bleu']:.4f}")

        # 결과 저장
        save_quality_results(quality_results)

    except FileNotFoundError:
        print(
            "테스트 데이터셋 파일을 찾을 수 없습니다. 'evaluate/test_dataset.json' 파일을 생성해주세요."
        )
    except Exception as e:
        print(f"평가 중 오류 발생: {str(e)}")
