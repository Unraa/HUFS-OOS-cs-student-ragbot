"""
마크다운 문서 처리, 임베딩 생성, RAG 챗봇 실행을 하나의 파이프라인으로 연결하는 스크립트
"""

import argparse
import os

from embeddings_generator import (generate_embeddings_for_chunks,
                                  load_vector_store, save_vector_store)
from markdown_processor import process_markdown_documents
from rag_chatbot import chat_interface


def setup_pipeline(docs_dir="study_docs", rebuild=False):
    """
    전체 파이프라인 설정 및 실행

    Args:
        docs_dir (str, optional): 문서가 저장된 디렉토리. 기본값은 "study_docs".
        rebuild (bool, optional): 벡터 저장소를 다시 구축할지 여부. 기본값은 False.
    """
    vector_store_path = "vector_store.json"
    combined_md_path = "docs/combined_markdown.md"

    # 벡터 저장소가 이미 존재하고 rebuild 플래그가 False인 경우, 기존 벡터 저장소 사용
    if os.path.exists(vector_store_path) and not rebuild:
        print(f"기존 벡터 저장소({vector_store_path})를 사용합니다.")
        return

    print("=== 마크다운 문서 처리 중... ===")
    _, chunks = process_markdown_documents(docs_dir, combined_md_path)

    print(f"\n=== 임베딩 생성 중 ({len(chunks)} 청크)... ===")
    chunks_with_embeddings = generate_embeddings_for_chunks(chunks)

    print("\n=== 벡터 저장소 저장 중... ===")
    save_vector_store(chunks_with_embeddings, vector_store_path)

    print("\n=== 파이프라인 설정 완료 ===")


def main():
    parser = argparse.ArgumentParser(
        description="마크다운 문서를 이용한 RAG 챗봇 파이프라인"
    )
    parser.add_argument(
        "--docs_dir",
        type=str,
        default="study_docs",
        help="마크다운 문서가 있는 디렉토리 경로 (기본값: study_docs)",
    )
    parser.add_argument(
        "--rebuild", action="store_true", help="벡터 저장소를 다시 구축합니다."
    )
    parser.add_argument(
        "--setup_only",
        action="store_true",
        help="벡터 저장소 설정만 수행하고 챗봇을 실행하지 않습니다.",
    )

    args = parser.parse_args()

    # 파이프라인 설정
    setup_pipeline(args.docs_dir, args.rebuild)

    # 챗봇 실행 (setup_only가 아닌 경우)
    if not args.setup_only:
        print("\n=== RAG 챗봇 시작 ===")
        chat_interface()


if __name__ == "__main__":
    main()
