from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, List, Optional
from pydantic import BaseModel

from app.services.embeddings import load_vector_store
from app.services.rag import generate_rag_response

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


# 벡터 스토어 로드 함수
def get_vector_store():
    vector_store = load_vector_store()
    if not vector_store:
        raise HTTPException(status_code=500, detail="벡터 저장소를 로드할 수 없습니다.")
    return vector_store


# RAG 쿼리 엔드포인트
@router.post("/query", response_model=QueryResponse)
async def query_rag(
    request: QueryRequest,
    vector_store: List[Dict] = Depends(get_vector_store),
):
    """
    사용자 쿼리에 대한 RAG 응답을 생성합니다.
    """
    try:
        answer = generate_rag_response(
            query=request.text,
            vector_store=vector_store,
            system_key=request.system_key,
        )

        return QueryResponse(
            answer=answer, source_chunks=None  # 필요한 경우 소스 청크도 반환할 수 있음
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"응답 생성 중 오류가 발생했습니다: {str(e)}"
        )
