from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, List, Optional
from pydantic import BaseModel

from app.services.rag import generate_rag_response, load_prompts, update_vector_store
from app.services.embeddings import get_or_create_collection
import logging

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
    collection = get_or_create_collection()
    if collection.count() == 0:
        raise HTTPException(
            status_code=500,
            detail="ChromaDB 컬렉션이 비어있습니다. 데이터를 추가해주세요.",
        )
    return collection


# RAG 쿼리 엔드포인트
@router.post("/query", response_model=QueryResponse)
async def query_rag(
    request: QueryRequest,
    collection: any = Depends(check_chromadb),
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
    return {"status": "ok"}


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
        collection = get_or_create_collection()
        if collection.count() == 0:
            raise HTTPException(
                status_code=500, detail="ChromaDB 컬렉션이 비어있습니다"
            )

        # RAG 응답 생성
        response = generate_rag_response(query)

        return {"response": response}
    except Exception as e:
        logging.error(f"채팅 처리 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"응답 생성 중 오류 발생: {str(e)}")


@router.post("/update-vector-store")
async def update_vector_store_endpoint():
    """
    벡터 저장소를 업데이트하는 엔드포인트
    """
    try:
        success = update_vector_store()
        if success:
            return {
                "status": "success",
                "message": "벡터 저장소가 성공적으로 업데이트되었습니다.",
            }
        else:
            raise HTTPException(status_code=500, detail="벡터 저장소 업데이트 실패")
    except Exception as e:
        logging.error(f"벡터 저장소 업데이트 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"벡터 저장소 업데이트 중 오류 발생: {str(e)}"
        )
