"""
테스트 데이터셋 생성 모듈

이 모듈은 RAG 시스템 평가를 위한 테스트 데이터셋을 생성하고 저장합니다.
"""

import json
import os
import sys
from typing import Dict, Any, List, Tuple

# 프로젝트 루트를 추가하여 app 모듈에 접근할 수 있도록 합니다
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from app.services.embeddings import find_similar_chunks, get_or_create_collection


def create_test_dataset() -> Dict[str, Any]:
    """
    평가용 테스트 데이터셋을 생성합니다.

    Returns:
        Dict[str, Any]: 테스트 데이터셋
    """
    # 샘플 테스트 데이터 (실제 사용 시에는 이 데이터를 실제 문서 ID와 맞게 수정해야 함)
    test_data = {
        "queries": [
            "컴퓨터공학과 졸업요건은 어떻게 되나요?",
            "전공필수 과목은 무엇인가요?",
            "컴공 학생회실은 어디에 있나요?",
            "코딩 동아리는 어떤 것이 있나요?",
            "교환학생 신청은 어떻게 하나요?",
            "교수님 연구실 위치가 어디인가요?",
            "장학금 신청은 어떻게 하나요?",
            "수강신청 기간은 언제인가요?",
            "컴퓨터공학과 학과장은 누구인가요?",
            "졸업 프로젝트는 어떻게 진행되나요?",
        ],
        "ground_truth_doc_ids": [
            ["chunk_1", "chunk_2"],  # 첫 번째 질의에 대한 정답 문서 ID
            ["chunk_3"],  # 두 번째 질의에 대한 정답 문서 ID
            ["chunk_4", "chunk_5"],
            ["chunk_6"],
            ["chunk_7", "chunk_8"],
            ["chunk_9"],
            ["chunk_10", "chunk_11"],
            ["chunk_12"],
            ["chunk_13"],
            ["chunk_14", "chunk_15"],
        ],
        "ground_truth_answers": [
            "컴퓨터공학과 졸업요건은 총 130학점 이상 이수, 전공 66학점 이상(필수 39학점, 선택 27학점), 교양 33학점 이상, 평균평점 1.75 이상입니다.",
            "전공필수 과목은 컴퓨터공학개론, 프로그래밍언어, 자료구조론, 알고리즘, 운영체제, 컴퓨터구조, 컴퓨터네트워크, 기초프로그래밍, 객체지향프로그래밍, 논리회로, 데이터베이스 등이 있습니다.",
            "컴퓨터공학과 학생회실은 공학관 321호에 위치해 있습니다.",
            "컴퓨터공학과 관련 동아리로는 웹 개발 동아리 '웹마스터', 게임 개발 동아리 'HUFS Game', 보안 동아리 'HUFS Security' 등이 있습니다.",
            "교환학생 신청은 국제교류팀을 통해 가능하며, 매 학기 시작 2-3개월 전에 공지가 나옵니다. 성적, 어학성적, 자기소개서 등을 준비해야 하며 학과 사무실을 통해 상담이 가능합니다.",
            "교수님 연구실은 공학관 3층과 4층에 위치해 있으며, 각 교수님별 연구실 호수는 학과 홈페이지에서 확인할 수 있습니다.",
            "장학금 신청은 학교 포털사이트를 통해 신청 기간에 온라인으로 신청하며, 성적장학금, 근로장학금, 외국어장학금 등 다양한 종류가 있습니다.",
            "수강신청 기간은 매 학기 시작 약 2주 전에 진행되며, 정확한 일정은 학사 일정을 참고하시기 바랍니다.",
            "현재 컴퓨터공학과 학과장은 홍길동 교수님이십니다. (가상 데이터)",
            "졸업 프로젝트는 4학년 1학기에 졸업프로젝트1, 2학기에 졸업프로젝트2를 수강하며, 지도교수님 지도하에 4-5명이 팀을 이루어 프로젝트를 진행합니다.",
        ],
    }

    return test_data


def save_test_dataset(output_file: str = "evaluate/test_dataset.json"):
    """
    테스트 데이터셋을 JSON 파일로 저장합니다.

    Args:
        output_file (str): 출력 파일 경로
    """
    # 테스트 데이터셋 생성
    test_data = create_test_dataset()

    # 디렉토리가 없으면 생성
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # JSON 파일로 저장
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)

    print(f"테스트 데이터셋이 {output_file}에 저장되었습니다.")
    print(
        "실제 평가를 위해서는 'ground_truth_doc_ids'를 현재 ChromaDB에 있는 문서 ID와 매핑해야 합니다."
    )


def find_best_match_for_answer(
    answer: str, top_k: int = 10
) -> Tuple[List[str], List[Dict]]:
    """
    정답에 가장 잘 매칭되는 문서를 ChromaDB에서 검색합니다.

    Args:
        answer (str): 정답 텍스트
        top_k (int, optional): 검색할 문서 수. 기본값은 10.

    Returns:
        Tuple[List[str], List[Dict]]: 문서 ID 목록과 전체 문서 정보
    """
    # 정답을 이용해 유사 문서 검색
    chunks = find_similar_chunks(answer, top_k=top_k)

    if not chunks:
        return [], []

    # 검색된 문서의 ID 목록 추출
    doc_ids = [chunk["id"] for chunk in chunks]

    return doc_ids, chunks


def auto_update_ground_truth_doc_ids(
    test_dataset_path: str = "evaluate/test_dataset.json", top_k: int = 5
) -> Dict[str, Any]:
    """
    테스트 데이터셋의 정답 문서 ID를 ChromaDB에서 자동으로 검색하여 업데이트합니다.

    Args:
        test_dataset_path (str): 테스트 데이터셋 파일 경로
        top_k (int): 각 질의당 검색할 최대 문서 수

    Returns:
        Dict[str, Any]: 업데이트된 테스트 데이터셋
    """
    print("ChromaDB에서 정답 문서 ID를 자동으로 검색하여 업데이트합니다...")

    # ChromaDB 컬렉션 확인
    collection = get_or_create_collection()
    if collection.count() == 0:
        print("ChromaDB 컬렉션이 비어 있습니다. 데이터를 먼저 추가해주세요.")
        return None

    # 테스트 데이터셋 로드
    try:
        with open(test_dataset_path, "r", encoding="utf-8") as f:
            test_data = json.load(f)
    except FileNotFoundError:
        print(f"테스트 데이터셋 파일({test_dataset_path})을 찾을 수 없습니다.")
        return None

    updated_doc_ids = []
    matching_details = []

    # 각 질의/정답에 대해 정답 문서 ID 자동 검색
    for i, (query, answer) in enumerate(
        zip(test_data["queries"], test_data["ground_truth_answers"])
    ):
        print(f"\n[{i+1}/{len(test_data['queries'])}] 질의: {query}")

        # 1. 먼저 질의로 검색
        query_ids, query_chunks = find_best_match_for_answer(query, top_k)

        # 2. 정답으로 검색
        answer_ids, answer_chunks = find_best_match_for_answer(answer, top_k)

        # 3. 중복 제거 및 병합 (질의 기반 결과 우선)
        all_ids = []
        seen_ids = set()

        # 질의 결과 먼저 추가
        for doc_id in query_ids:
            if doc_id not in seen_ids:
                all_ids.append(doc_id)
                seen_ids.add(doc_id)

        # 정답 결과 추가
        for doc_id in answer_ids:
            if doc_id not in seen_ids:
                all_ids.append(doc_id)
                seen_ids.add(doc_id)

        # 상위 3개만 사용
        final_ids = all_ids[:3]
        updated_doc_ids.append(final_ids)

        # 결과 출력
        print(f"  - 기존 정답 문서 ID: {test_data['ground_truth_doc_ids'][i]}")
        print(f"  - 자동 검색된 문서 ID: {final_ids}")

        # 매칭 상세 정보 저장
        matching_details.append(
            {
                "query": query,
                "answer": answer,
                "original_ids": test_data["ground_truth_doc_ids"][i],
                "found_ids": final_ids,
                "query_search_results": [
                    {"id": c["id"], "title": c["title"]} for c in query_chunks[:3]
                ],
                "answer_search_results": [
                    {"id": c["id"], "title": c["title"]} for c in answer_chunks[:3]
                ],
            }
        )

    # 데이터셋 업데이트
    test_data["ground_truth_doc_ids"] = updated_doc_ids

    # 업데이트된 데이터셋 저장
    with open(test_dataset_path, "w", encoding="utf-8") as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)

    # 매칭 상세 정보 저장
    matching_details_path = os.path.join(
        os.path.dirname(test_dataset_path), "doc_id_matching_details.json"
    )
    with open(matching_details_path, "w", encoding="utf-8") as f:
        json.dump(matching_details, f, ensure_ascii=False, indent=2)

    print(f"\n테스트 데이터셋이 {test_dataset_path}에 업데이트되었습니다.")
    print(f"매칭 상세 정보가 {matching_details_path}에 저장되었습니다.")

    return test_data


def update_ground_truth_doc_ids(test_dataset_file: str = "evaluate/test_dataset.json"):
    """
    테스트 데이터셋의 정답 문서 ID를 실제 ChromaDB 문서 ID로 업데이트합니다.
    자동 또는 수동 업데이트를 선택할 수 있습니다.

    Args:
        test_dataset_file (str): 테스트 데이터셋 파일 경로
    """
    print("정답 문서 ID 업데이트 방법을 선택하세요:")
    print("1. 자동 업데이트 (ChromaDB 검색 기반)")
    print("2. 수동 업데이트 (사용자 입력)")

    try:
        choice = input("선택 (1/2): ").strip()

        if choice == "1":
            auto_update_ground_truth_doc_ids(test_dataset_file)
            return

        elif choice == "2":
            # 기존 테스트 데이터셋 로드
            try:
                with open(test_dataset_file, "r", encoding="utf-8") as f:
                    test_data = json.load(f)
            except FileNotFoundError:
                print(f"테스트 데이터셋 파일({test_dataset_file})을 찾을 수 없습니다.")
                return

            for i, query in enumerate(test_data["queries"]):
                print(f"\n질의: {query}")
                print(f"현재 정답 문서 ID: {test_data['ground_truth_doc_ids'][i]}")
                print("새 정답 문서 ID를 입력하세요 (쉼표로 구분):")
                new_ids = input().strip()

                if new_ids:
                    test_data["ground_truth_doc_ids"][i] = new_ids.split(",")

            # 업데이트된 데이터셋 저장
            with open(test_dataset_file, "w", encoding="utf-8") as f:
                json.dump(test_data, f, ensure_ascii=False, indent=2)

            print(f"테스트 데이터셋이 {test_dataset_file}에 업데이트되었습니다.")

        else:
            print("잘못된 선택입니다. 1 또는 2를 입력하세요.")

    except Exception as e:
        print(f"업데이트 중 오류 발생: {str(e)}")


if __name__ == "__main__":
    # 테스트 데이터셋 생성 및 저장
    save_test_dataset()

    # 정답 문서 ID 업데이트 (선택 사항)
    print("\n정답 문서 ID를 업데이트하시겠습니까? (y/n)")
    if input().lower() == "y":
        update_ground_truth_doc_ids()
