import os
import time

import streamlit as st
from embeddings_generator import load_vector_store
from rag_chatbot import generate_rag_response, load_prompts
from utils import get_openai_client

# 페이지 설정
st.set_page_config(
    page_title="한국외국어대학교 컴퓨터공학부 RAG 챗봇",
    page_icon="💬",
    layout="centered",
)

# 스타일 설정
st.markdown(
    """
<style>
.chat-message {
    padding: 1.5rem; 
    border-radius: 0.5rem; 
    margin-bottom: 1rem; 
    display: flex;
    flex-direction: row;
    align-items: flex-start;
}
.chat-message.user {
    background-color: #F0F2F6;
}
.chat-message.bot {
    background-color: #E8F4FE;
}
.chat-message .avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: cover;
    margin-right: 1rem;
}
.chat-message .message {
    flex: 1;
}
.stTextInput {
    position: fixed;
    bottom: 3rem;
    background-color: white;
    left: 0;
    right: 0;
    padding: 1rem 5rem;
}
</style>
""",
    unsafe_allow_html=True,
)

# 시스템 프롬프트 로드 확인
try:
    prompts = load_prompts()
    if "system_prompts" in prompts and "rag" in prompts["system_prompts"]:
        st.session_state.prompts_loaded = True
    else:
        st.session_state.prompts_loaded = False
except Exception as e:
    st.error(f"프롬프트 로드 중 오류 발생: {str(e)}")
    st.session_state.prompts_loaded = False

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

if "vector_store" not in st.session_state:
    # 벡터 저장소 로드
    try:
        vector_store = load_vector_store()
        if vector_store:
            st.session_state.vector_store = vector_store
            st.session_state.vector_store_loaded = True
        else:
            st.session_state.vector_store_loaded = False
    except Exception as e:
        st.error(f"벡터 저장소 로드 중 오류 발생: {str(e)}")
        st.session_state.vector_store_loaded = False

# 제목 및 소개
st.title("한국외국어대학교 컴퓨터공학부 RAG 챗봇")

# 로드 상태 표시
status_messages = []

if not st.session_state.get("prompts_loaded", False):
    status_messages.append("⚠️ 프롬프트 로드 실패: 'code/prompts.yaml' 파일 확인 필요")
else:
    status_messages.append("✅ 프롬프트 로드 성공")

if not st.session_state.get("vector_store_loaded", False):
    status_messages.append(
        "⚠️ 벡터 저장소 로드 실패: 'vector_store.json' 파일 확인 필요"
    )
else:
    status_messages.append(
        f"✅ 벡터 저장소 로드 성공: {len(st.session_state.vector_store)}개 청크"
    )

if status_messages:
    status_text = "\n".join(status_messages)
    if "⚠️" in status_text:
        st.warning(status_text)
    else:
        st.success(status_text)

# 필수 구성 요소가 모두 로드되었는지 확인
can_respond = st.session_state.get(
    "vector_store_loaded", False
) and st.session_state.get("prompts_loaded", False)
if not can_respond:
    st.error("일부 구성 요소가 로드되지 않아 챗봇 기능이 제한됩니다.")

# 대화 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("질문을 입력하세요"):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 새 메시지 표시
    with st.chat_message("user"):
        st.markdown(prompt)

    # 봇 응답 생성
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        if can_respond:
            try:
                # 실제 응답 생성
                response = generate_rag_response(prompt, st.session_state.vector_store)

                # 타이핑 효과
                for chunk in response.split():
                    full_response += chunk + " "
                    message_placeholder.markdown(full_response + "▌")
                    time.sleep(0.01)

                message_placeholder.markdown(full_response)

                # 응답 저장
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )
            except Exception as e:
                error_msg = f"응답 생성 중 오류가 발생했습니다: {str(e)}"
                message_placeholder.markdown(error_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_msg}
                )
        else:
            error_msg = "필요한 리소스가 로드되지 않아 응답을 생성할 수 없습니다."
            message_placeholder.markdown(error_msg)
            st.session_state.messages.append(
                {"role": "assistant", "content": error_msg}
            )

# 사이드바 정보
with st.sidebar:
    st.header("정보")
    st.markdown(
        """
    이 챗봇은 한국외국어대학교 컴퓨터공학부 관련 문서를 기반으로 RAG(Retrieval-Augmented Generation) 기술을 활용하여 
    질문에 답변합니다.
    
    **주요 기능:**
    - 마크다운 문서 기반 지식 활용
    - 임베딩 벡터와 코사인 유사도를 통한 관련 정보 검색
    - OpenAI API를 활용한 응답 생성
    """
    )

    st.header("사용 방법")
    st.markdown(
        """
    아래와 같은 질문을 시도해보세요:
    - 컴퓨터공학부 졸업 요건은 무엇인가요?
    - 학과의 주요 교과목은 무엇인가요?
    - 대학원 입학 요건은 어떻게 되나요?
    """
    )

    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.rerun()

# 앱 실행 명령어: streamlit run code/web_ui.py
