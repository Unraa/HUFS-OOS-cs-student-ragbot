import os
from typing import Dict, List

import yaml
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain.vectorstores import Chroma
try:
    from langchain.schema import Document
except ImportError:
    from langchain_core.documents import Document

from app.core.config import settings


def load_prompts(yaml_file=None):
    """
    YAML 파일에서 프롬프트를 로드하는 함수

    Args:
        yaml_file (str): YAML 파일 경로

    Returns:
        dict: 로드된 프롬프트
    """
    if yaml_file is None:
        yaml_file = settings.PROMPTS_FILE

    with open(yaml_file, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def get_vector_store():
    """
    ChromaDB 벡터 저장소를 가져옵니다.

    Returns:
        Chroma: ChromaDB 벡터 저장소 인스턴스
    """
    embeddings = OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL, openai_api_key=settings.OPENAI_API_KEY
    )

    # ChromaDB 디렉토리가 존재하는지 확인
    if not os.path.exists(settings.CHROMA_DB_DIR):
        print(f"ChromaDB 디렉토리가 존재하지 않습니다: {settings.CHROMA_DB_DIR}")
        print("벡터 저장소를 먼저 업데이트해주세요.")
        os.makedirs(settings.CHROMA_DB_DIR, exist_ok=True)

    vector_store = Chroma(
        collection_name=settings.CHROMA_COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=settings.CHROMA_DB_DIR,
    )

    return vector_store


def create_rag_chain():
    """
    RAG 체인을 생성합니다.

    Returns:
        RetrievalQA: RAG 체인 인스턴스
    """
    # LLM 초기화
    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=settings.TEMPERATURE,
        max_tokens=settings.MAX_TOKENS,
        openai_api_key=settings.OPENAI_API_KEY,
    )

    # 벡터 저장소 가져오기
    vector_store = get_vector_store()

    # 리트리버 생성
    retriever = vector_store.as_retriever(search_kwargs={"k": settings.RETRIEVAL_K})

    # RAG 체인 생성
    rag_chain = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True
    )

    return rag_chain


def update_vector_store(documents_dir=None):
    """
    마크다운 문서를 처리하고 ChromaDB 벡터 저장소를 업데이트합니다.

    Args:
        documents_dir (str, optional): 마크다운 문서 디렉토리

    Returns:
        bool: 업데이트 성공 여부
    """
    from app.services.markdown_processor import process_markdown_documents

    if documents_dir is None:
        documents_dir = settings.DOCS_DIR

    print(f"마크다운 문서를 처리하고 벡터 저장소를 업데이트합니다...")

    try:
        # 마크다운 문서 처리
        documents, chunks = process_markdown_documents(documents_dir)

        if not chunks:
            print("처리할 문서가 없습니다.")
            return False

        print(f"{len(chunks)}개의 청크로 분할되었습니다. 벡터 저장소에 저장 중...")

        # 임베딩 및 벡터 저장소 생성
        embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL, openai_api_key=settings.OPENAI_API_KEY
        )

        # 기존 컬렉션 삭제 후 새로 생성
        try:
            # 기존 벡터 저장소가 있다면 삭제
            import shutil

            if os.path.exists(settings.CHROMA_DB_DIR):
                shutil.rmtree(settings.CHROMA_DB_DIR)
                print("기존 벡터 저장소를 삭제했습니다.")
        except Exception as e:
            print(f"기존 벡터 저장소 삭제 중 오류: {str(e)}")

        # ChromaDB에 문서 저장
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name=settings.CHROMA_COLLECTION_NAME,
            persist_directory=settings.CHROMA_DB_DIR,
        )

        print(f"벡터 저장소 업데이트가 완료되었습니다.")
        return True

    except Exception as e:
        print(f"벡터 저장소 업데이트 중 오류 발생: {str(e)}")
        return False


def generate_rag_response(query: str, system_key: str = "rag") -> str:
    """
    RAG 접근 방식을 사용하여 사용자 쿼리에 응답을 생성합니다.

    Args:
        query (str): 사용자 쿼리
        system_key (str, optional): 시스템 프롬프트 키. 기본값은 "rag".

    Returns:
        str: 생성된 응답
    """
    try:
        # 벡터 저장소 확인
        vector_store = get_vector_store()
        try:
            count = vector_store._collection.count()
            if count == 0:
                return "죄송합니다. 벡터 저장소가 비어있습니다. 먼저 문서를 업데이트해주세요."
        except Exception as e:
            return f"벡터 저장소 접근 중 오류가 발생했습니다: {str(e)}"

        # 프롬프트 로드
        try:
            prompts = load_prompts()
            system_prompt = prompts["system_prompts"][system_key]
        except Exception as e:
            print(f"프롬프트 로드 오류: {str(e)}")
            system_prompt = "당신은 한국외국어대학교 컴퓨터공학과 관련 질문에 답변하는 도우미입니다."

        # 방법 1: RetrievalQA 체인 사용 (우선 시도)
        try:
            rag_chain = create_rag_chain()
            enhanced_query = f"{system_prompt}\n\n질문: {query}"
            result = rag_chain.invoke({"query": enhanced_query})
            return result["result"]
        except Exception as chain_error:
            print(f"RetrievalQA 체인 오류: {str(chain_error)}")

            # 방법 2: 직접 검색 및 응답 생성 (fallback)
            try:
                # 관련 문서 검색
                docs = vector_store.similarity_search(query, k=settings.RETRIEVAL_K)

                if not docs:
                    return "죄송합니다. 관련된 정보를 찾을 수 없습니다."

                # 컨텍스트 구성
                context = "\n\n".join([doc.page_content for doc in docs])

                # LLM으로 직접 응답 생성
                llm = ChatOpenAI(
                    model=settings.LLM_MODEL,
                    temperature=settings.TEMPERATURE,
                    max_tokens=settings.MAX_TOKENS,
                    openai_api_key=settings.OPENAI_API_KEY,
                )

                messages = [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"다음 컨텍스트를 바탕으로 질문에 답변해주세요.\n\n컨텍스트:\n{context}\n\n질문: {query}",
                    },
                ]

                response = llm.invoke(messages)
                return response.content

            except Exception as fallback_error:
                print(f"Fallback 방법도 실패: {str(fallback_error)}")
                return f"죄송합니다. 응답을 생성하는 중에 오류가 발생했습니다: {str(fallback_error)}"

    except Exception as e:
        print(f"응답 생성 중 오류 발생: {str(e)}")
        return f"죄송합니다. 응답을 생성하는 중에 오류가 발생했습니다: {str(e)}"


def chat_interface():
    """
    사용자와 대화형 인터페이스를 제공하는 함수
    """
    print("한국외국어대학교 컴퓨터공학과 RAG 챗봇에 오신 것을 환영합니다!")
    print("종료하려면 'quit', 'exit', '종료' 중 하나를 입력하세요.")
    print("-" * 50)

    # 벡터 저장소 확인
    try:
        vector_store = get_vector_store()
        count = vector_store._collection.count()

        if count > 0:
            print(f"ChromaDB에서 {count}개의 청크가 로드되었습니다.")
        else:
            print("ChromaDB가 비어있습니다. 데이터를 추가해주세요.")
            return
    except Exception as e:
        print(f"벡터 저장소 확인 중 오류 발생: {str(e)}")
        return

    while True:
        user_input = input("\n질문을 입력하세요: ")

        if user_input.lower() in ["quit", "exit", "종료"]:
            print("챗봇을 종료합니다. 감사합니다!")
            break

        if not user_input.strip():
            print("질문을 입력해주세요.")
            continue

        print("처리 중...")
        response = generate_rag_response(user_input)
        print("\n답변:", response)


# 기존 함수들과의 호환성을 위한 래퍼 함수들
def format_context_from_chunks(chunks: List[Dict]) -> str:
    """기존 코드와의 호환성을 위한 래퍼 함수"""
    formatted_context = (
        "다음은 한국외국어대학교 컴퓨터공학과 관련 문서에서 검색된 내용입니다:\n\n"
    )

    for i, chunk in enumerate(chunks, 1):
        formatted_context += f"--- 문서 {i}: {chunk['title']} ---\n"
        formatted_context += chunk["content"]
        formatted_context += "\n\n"

    return formatted_context
