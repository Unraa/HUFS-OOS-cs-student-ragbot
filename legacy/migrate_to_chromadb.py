#!/usr/bin/env python
"""
기존 JSON 벡터 저장소에서 ChromaDB로 데이터를 마이그레이션하는 스크립트
"""

import json
import os
import sys

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from app.core.config import settings
from app.services.embeddings import (get_or_create_collection,
                                     load_vector_store,
                                     migrate_json_to_chromadb)


def main():
    """
    JSON 벡터 저장소에서 ChromaDB로 데이터를 마이그레이션합니다.
    """
    print("=" * 60)
    print("JSON 벡터 저장소에서 ChromaDB로 마이그레이션 시작")
    print("=" * 60)

    # JSON 벡터 저장소 로드
    json_path = settings.VECTOR_STORE_PATH

    if not os.path.exists(json_path):
        print(f"오류: 벡터 저장소 파일을 찾을 수 없습니다: {json_path}")
        return False

    try:
        # 벡터 저장소 로드 - 이 함수가 자동으로 마이그레이션 시도
        vector_store = load_vector_store()

        # ChromaDB 확인
        collection = get_or_create_collection()
        count = collection.count()

        if count > 0:
            print(f"마이그레이션 성공: ChromaDB에 {count}개의 청크가 저장되었습니다.")
            return True
        else:
            print("마이그레이션 실패: ChromaDB에 데이터가 저장되지 않았습니다.")
            return False

    except Exception as e:
        print(f"마이그레이션 중 오류 발생: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()

    if success:
        print("\n마이그레이션이 성공적으로 완료되었습니다.")
        print("이제 ChromaDB를 사용하여 검색을 수행할 수 있습니다.")
    else:
        print("\n마이그레이션이 실패했습니다.")
        print("문제를 해결한 후 다시 시도하세요.")

    sys.exit(0 if success else 1)
