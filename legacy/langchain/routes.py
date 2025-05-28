import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel

from app.services.rag import (generate_rag_response, get_vector_store,
                              load_prompts, update_vector_store)

# 라우터 정의
router = APIRouter(
    prefix="/api",
    tags=["rag"],
    responses={404: {"description": "Not found"}},
)


# 요청/응답 모델
class QueryRequest(BaseModel):
    text: str
    system_key: Optional[str] = "rag"


class QueryResponse(BaseModel):
    answer: str
    source_chunks: Optional[List[Dict]] = None


# ChromaDB 컬렉션 확인 함수
def check_chromadb():
    """ChromaDB 벡터 저장소 상태를 확인합니다."""
    try:
        vector_store = get_vector_store()
        try:
            count = vector_store._collection.count()

            if count == 0:
                raise HTTPException(
                    status_code=500,
                    detail="ChromaDB 컬렉션이 비어있습니다. 데이터를 추가해주세요.",
                )
            return vector_store
        except AttributeError:
            # _collection 속성이 없는 경우 대체 방법 시도
            try:
                # 간단한 검색으로 데이터 존재 여부 확인
                results = vector_store.similarity_search("test", k=1)
                if not results:
                    raise HTTPException(
                        status_code=500,
                        detail="ChromaDB 컬렉션이 비어있습니다. 데이터를 추가해주세요.",
                    )
                return vector_store
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"ChromaDB 상태 확인 중 오류: {str(e)}",
                )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"ChromaDB 연결 오류: {str(e)}",
        )


# RAG 쿼리 엔드포인트
@router.post("/query", response_model=QueryResponse)
async def query_rag(
    request: QueryRequest,
    vector_store: any = Depends(check_chromadb),
):
    """
    사용자 쿼리에 대한 RAG 응답을 생성합니다.
    """
    try:
        answer = generate_rag_response(
            query=request.text,
            system_key=request.system_key,
        )

        return QueryResponse(
            answer=answer, source_chunks=None  # 필요한 경우 소스 청크도 반환할 수 있음
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"응답 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """상태 확인 엔드포인트"""
    try:
        vector_store = get_vector_store()
        try:
            count = vector_store._collection.count()
        except AttributeError:
            # _collection 속성이 없는 경우 대체 방법
            try:
                results = vector_store.similarity_search("test", k=1)
                count = len(results) if results else 0
            except:
                count = "unknown"

        return {
            "status": "ok",
            "vector_store_count": count,
            "message": "Langchain RAG 시스템이 정상 작동 중입니다.",
            "system": "langchain",
        }
    except Exception as e:
        return {"status": "error", "message": f"시스템 오류: {str(e)}"}


@router.post("/chat")
async def chat(message: dict = Body(...)):
    """
    채팅 메시지를 처리하고 RAG 기반 응답을 반환하는 엔드포인트
    """
    try:
        # 요청에서 메시지 추출
        query = message.get("message", "")
        if not query:
            raise HTTPException(status_code=400, detail="메시지 내용이 없습니다")

        # ChromaDB 확인
        vector_store = get_vector_store()
        try:
            count = vector_store._collection.count()
        except AttributeError:
            try:
                results = vector_store.similarity_search("test", k=1)
                count = len(results) if results else 0
            except:
                count = 0

        if count == 0:
            raise HTTPException(
                status_code=500, detail="ChromaDB 컬렉션이 비어있습니다"
            )

        # RAG 응답 생성 (Langchain 체인 사용)
        response = generate_rag_response(query)

        return {
            "response": response,
            "metadata": {"vector_store_count": count, "system": "langchain"},
        }
    except Exception as e:
        logging.error(f"채팅 처리 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"응답 생성 중 오류 발생: {str(e)}")


@router.post("/update-vector-store")
@router.get("/update-vector-store")
async def update_vector_store_endpoint():
    """
    벡터 저장소를 업데이트하는 엔드포인트
    GET 또는 POST 요청을 통해 호출 가능합니다.
    """
    try:
        success = update_vector_store()
        if success:
            # 업데이트 후 벡터 저장소 상태 확인
            try:
                vector_store = get_vector_store()
                try:
                    count = vector_store._collection.count()
                except AttributeError:
                    try:
                        results = vector_store.similarity_search("test", k=1)
                        count = len(results) if results else 0
                    except:
                        count = "unknown"

                return {
                    "status": "success",
                    "message": "Langchain을 사용하여 벡터 저장소가 성공적으로 업데이트되었습니다.",
                    "document_count": count,
                    "system": "langchain",
                }
            except Exception as e:
                return {
                    "status": "success",
                    "message": "벡터 저장소 업데이트는 완료되었으나 상태 확인 중 오류가 발생했습니다.",
                    "error": str(e),
                }
        else:
            raise HTTPException(status_code=500, detail="벡터 저장소 업데이트 실패")
    except Exception as e:
        logging.error(f"벡터 저장소 업데이트 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"벡터 저장소 업데이트 중 오류 발생: {str(e)}"
        )
