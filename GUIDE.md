# HUFS CS 학생 챗봇 실행 및 테스트 가이드

이 가이드는 한국외국어대학교 컴퓨터공학과 정보 제공 챗봇 프로젝트를 처음 실행하고 테스트하는 방법을 설명합니다.

## 1. 프로젝트 개요

이 프로젝트는 RAG(Retrieval-Augmented Generation) 아키텍처를 기반으로 한국외국어대학교 컴퓨터공학과 관련 정보를 제공하는 챗봇입니다. 학과 사이트나 사무실 문의 없이도 주요 정보를 챗봇을 통해 간편히 확인할 수 있습니다.

### 주요 기능

- 컴퓨터공학과 관련 정보 질의응답 (졸업 요건, 이수 기준 등)
- 내부 문서 기반 RAG 검색 시스템
- ChatGPT 스타일 웹 인터페이스

## 2. 시스템 요구사항

- **Python**: 3.10 이상
- **운영체제**: Windows, macOS, Linux (모든 주요 OS 지원)
- **OpenAI API 키**: 응답 생성을 위해 필요합니다.
- **필수 라이브러리**: requirements.txt 참조

## 3. 환경 설정

### 3.1. 프로젝트 클론

```bash
git clone https://github.com/your-username/HUFS-OOS-cs-student-ragbot.git
cd HUFS-OOS-cs-student-ragbot
```

### 3.2. 가상환경 설정

```bash
# conda 환경 생성 및 활성화
conda create -n HUFS-OOS-cs-student-ragbot python=3.10
conda activate HUFS-OOS-cs-student-ragbot
```

### 3.3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3.4. 환경 변수 설정

1. 프로젝트 루트에 `.env` 파일을 다음과 같이 생성하세요:

```
OPENAI_API_KEY=your_openai_api_key_here
```

## 4. 프로젝트 구조

```
HUFS-OOS-cs-student-ragbot/
│
├── main.py                            # FastAPI 애플리케이션 진입점
├── launch.sh                          # 서비스 실행 스크립트
│
├── app/                               # 애플리케이션 코드
│   ├── api/                           # API 라우터
│   ├── core/                          # 핵심 구성요소
│   ├── services/                      # 비즈니스 로직
│   └── python_web/                    # Streamlit 웹 인터페이스 (개발용)
│
├── client_web/                        # 클라이언트 웹 코드
│   ├── env/                           # 클라이언트 웹 가상환경
│   └── index.html                     # ChatGPT 스타일 웹 인터페이스
│
├── data/                              # 데이터 파일
│   ├── vector_store.json              # 벡터 저장소
│   └── docs/                          # 문서 디렉토리
│       ├── raw/                       # 원본 문서 디렉토리
│       └── combined_markdown.md       # 결합된 마크다운 파일
```

## 5. 실행 방법

### 5.1. 권장 실행 방법 - launch.sh 스크립트 사용

프로젝트 루트 디렉토리에서 launch.sh 스크립트를 실행하여 서비스를 시작하는 것이 권장됩니다:

```bash
# 실행 권한 부여 (최초 1회)
chmod +x launch.sh

# 실행
./launch.sh
```

launch.sh 스크립트는 FastAPI 서버를 실행하며, 모든 필요한 환경 설정을 자동으로 처리합니다.

실행 후 다음 URL에서 서비스에 접근할 수 있습니다:

- 메인 페이지: http://localhost:8000
- FastAPI 문서: http://localhost:8000/docs
- ChatGPT 스타일 UI: http://localhost:8000/chat

### 5.2. 직접 FastAPI 서버 실행 (대체 방법)

필요한 경우 직접 uvicorn 명령으로 FastAPI 서버를 실행할 수도 있습니다:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 6. 사용 방법

### 6.1. ChatGPT 스타일 웹 인터페이스

1. 브라우저에서 http://localhost:8000 접속
2. "ChatGPT 스타일 웹 인터페이스" 링크 클릭 또는 직접 http://localhost:8000/chat 접속
3. 채팅 창에 질문 입력 후 엔터 또는 전송 버튼 클릭

웹 인터페이스는 현대적인 채팅 UI를 제공하며, 직관적인 사용자 경험을 위해 설계되었습니다:

- 입력 중 표시 애니메이션
- 이전 대화 내역 유지
- 모바일 친화적 디자인

## 7. 테스트 질문 예시

다음과 같은 질문으로 챗봇을 테스트해볼 수 있습니다:

- 컴퓨터공학과 졸업 요건은 무엇인가요?
- 학과의 주요 교과목은 무엇인가요?
- 대학원 입학 요건은 어떻게 되나요?
- 전공필수 과목은 어떤 것들이 있나요?
- 학과 교수진은 어떻게 구성되어 있나요?
- 컴퓨터공학과 사무실 위치는 어디인가요?

## 8. 문제 해결

### 8.1. 벡터 저장소 로드 실패

벡터 저장소가 로드되지 않을 경우, 다음을 확인하세요:

1. `data/vector_store.json` 파일이 존재하는지 확인
2. 파일이 없다면, 임베딩을 처음부터 생성해야 합니다. 개발 중인 경우 팀원에게 문의하세요.

### 8.2. OpenAI API 오류

OpenAI API 관련 오류가 발생하는 경우:

1. `.env` 파일이 프로젝트 루트에 존재하는지 확인
2. `OPENAI_API_KEY`가 올바르게 설정되었는지 확인
3. API 키가 유효한지 확인 (크레딧 소진 여부 등)

### 8.3. CORS 오류

웹 인터페이스에서 API 호출 시 CORS 오류가 발생하는 경우:

1. `main.py`에서 CORS 설정을 확인하세요
2. 개발 환경에서는 `allow_origins=["*"]`로 설정되어 있습니다
3. 실제 배포 환경에서는 적절한 출처만 허용하도록 설정해야 합니다

## 9. 기여 방법

프로젝트 기여에 관심이 있다면 README.md의 개발 방식을 참고하세요. 주요 규칙:

1. 저장소를 Fork하세요
2. 기능 브랜치를 생성하세요 (`feature/기능명`)
3. PR을 `dev` 브랜치로 생성하세요

## 10. 참고 자료

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [RAG(Retrieval-Augmented Generation) 관련 자료](https://www.pinecone.io/learn/retrieval-augmented-generation/)

## 벡터 데이터베이스 사용 안내

### ChromaDB와 FAISS 벡터 검색

최근 업데이트에서 프로젝트는 JSON 파일 기반 벡터 스토어에서 ChromaDB와 FAISS를 사용한 벡터 데이터베이스 시스템으로 전환되었습니다. 이로써 검색 성능이 향상되고, 대규모 데이터 처리가 가능해졌습니다.

#### 설치 및 실행

ChromaDB와 FAISS를 사용하기 위해 필요한 패키지는 `requirements.txt`에 포함되어 있습니다:

```bash
pip install -r requirements.txt
```

#### 데이터 저장 위치

ChromaDB는 데이터를 `data/chroma_db` 디렉토리에 저장합니다. 이 디렉토리는 자동으로 생성되며, 벡터 데이터와 메타데이터를 저장합니다.

#### 문서 업데이트 방법

새로운 문서를 추가하거나 기존 문서를 업데이트하려면 `data/docs` 디렉토리에 마크다운(.md) 파일을 추가하거나 수정한 후, 다음 명령어를 실행하세요:

```python
# Python 인터프리터에서
from app.services.rag import update_vector_store
update_vector_store()

# 또는 FastAPI 인터페이스의 '/update-vector-store' 엔드포인트를 사용할 수 있습니다.
```

#### 레거시 코드

기존 JSON 기반 벡터 스토어 코드는 `legacy` 폴더에 보관되어 있습니다. 새로운 개발에는 ChromaDB 기반 코드를 사용하는 것을 권장합니다.
