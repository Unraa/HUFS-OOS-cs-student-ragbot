# Langchain 리팩토링 버전

이 폴더는 기존 RAG 시스템을 Langchain으로 리팩토링한 버전입니다.

## 주요 변경사항

### 1. 패키지 추가 (requirements.txt)

```
# Langchain 관련 패키지
langchain
langchain-openai
langchain-community
langchain-chroma
```

### 2. 설정 추가 (config.py)

```python
# Langchain 설정
CHUNK_SIZE: int = 1000
CHUNK_OVERLAP: int = 200
RETRIEVAL_K: int = 5
TEMPERATURE: float = 0.3
MAX_TOKENS: int = 1000

# API 키 검증 로직 추가
def validate_api_key(self):
    """OpenAI API 키 유효성 검사"""
```

### 3. 문서 처리 개선 (markdown_processor.py)

- `DirectoryLoader`와 `TextLoader` 사용
- `RecursiveCharacterTextSplitter`로 청킹
- Langchain `Document` 객체 사용
- 향상된 오류 처리 및 로깅
- **빈 문서 및 짧은 문서 필터링 (50자 미만 제외)**
- **유효한 청크만 반환하도록 개선**

### 4. RAG 시스템 개선 (rag.py)

- `RetrievalQA` 체인 사용
- `ChatOpenAI`와 `OpenAIEmbeddings` 사용
- `Chroma` 벡터 저장소 통합
- 벡터 저장소 상태 확인 및 오류 처리 개선
- **이중 fallback 시스템**: RetrievalQA 실패 시 직접 검색 방식 사용
- **ChromaDB 디렉토리 자동 생성**

### 5. API 라우트 개선 (routes.py)

- Langchain 체인을 사용한 응답 생성
- 향상된 오류 처리 및 메타데이터 제공
- 벡터 저장소 접근 방식 개선

## 장점

1. **코드 간소화**: Langchain의 추상화로 코드가 더 간결해짐
2. **유지보수성**: 표준화된 인터페이스로 유지보수 용이
3. **확장성**: 다양한 LLM과 벡터 저장소 쉽게 교체 가능
4. **개발 효율성**: 검증된 컴포넌트 사용으로 개발 시간 단축
5. **안정성**: 다중 fallback 시스템으로 높은 안정성 확보

## 단점

1. **성능 오버헤드**: 추가 추상화 레이어로 인한 약간의 성능 저하
2. **제어 제한**: 세밀한 제어가 어려울 수 있음
3. **의존성 증가**: 추가 패키지 의존성

## 사용법

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일에 OpenAI API 키 설정:

```
OPENAI_API_KEY=sk-your-api-key-here
```

### 3. 파일 교체

기존 파일들을 이 폴더의 파일들로 교체:

- `app/core/config.py`
- `app/services/markdown_processor.py`
- `app/services/rag.py`
- `app/api/routes.py`

### 4. 서버 실행

```bash
python main.py
```

## 호환성 참고사항

- 기존 함수들과의 호환성을 위한 래퍼 함수들이 포함되어 있습니다.
- 기존 API 엔드포인트는 동일하게 유지됩니다.
- ChromaDB 데이터는 기존과 호환됩니다.

## 문제 해결

### 1. 임포트 오류

**Document 클래스 임포트 오류:**

```python
try:
    from langchain.schema import Document
except ImportError:
    from langchain_core.documents import Document
```

**Chroma 임포트 오류:**

```python
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain.vectorstores import Chroma
```

### 2. 벡터 저장소 접근 오류

`_collection` 속성 접근 오류가 발생하는 경우:

- 대체 방법으로 `similarity_search`를 사용하여 데이터 존재 여부 확인
- 코드에 이미 fallback 로직이 포함되어 있음

### 3. RetrievalQA 체인 오류

RetrievalQA 체인이 실패하는 경우:

- 자동으로 직접 검색 방식으로 fallback
- 두 방법 모두 실패 시 상세한 오류 메시지 제공

### 4. 문서 로드 실패

문서 로드 중 오류가 발생하는 경우:

- 각 파일 타입별로 개별 try-catch 처리
- 일부 파일 로드 실패 시에도 다른 파일들은 정상 처리
- 50자 미만의 짧은 문서는 자동으로 필터링

### 5. 벡터 저장소 업데이트 오류

벡터 저장소 업데이트 시 문제가 발생하는 경우:

- 기존 벡터 저장소 디렉토리를 완전히 삭제 후 재생성
- 단계별 오류 처리 및 로깅
- ChromaDB 디렉토리 자동 생성

### 6. API 키 오류

OpenAI API 키 관련 문제:

- 시작 시 자동으로 API 키 유효성 검사
- 잘못된 키 형식 감지 및 경고 메시지 제공

## 실제 테스트 결과

이 리팩토링 버전은 다음과 같은 실제 문제들을 해결했습니다:

1. **임포트 오류**:

   - `MarkdownLoader` 대신 `TextLoader` 사용
   - Langchain 버전별 임포트 경로 차이 해결
   - `langchain.schema` vs `langchain_core.documents` 호환성

2. **벡터 저장소 접근**:

   - `_collection` 속성 접근 실패 시 대체 방법 제공
   - ChromaDB 초기화 오류 처리

3. **RAG 체인 안정성**:

   - RetrievalQA 체인 실패 시 직접 검색 방식으로 fallback
   - 이중 안전장치로 높은 안정성 확보

4. **문서 품질 관리**:

   - 빈 문서 및 짧은 문서 자동 필터링
   - 유효한 청크만 벡터 저장소에 저장

5. **오류 처리**:

   - 각 단계별 세밀한 오류 처리 및 복구 로직
   - 상세한 로그 메시지로 디버깅 용이성 향상

6. **환경 설정**:
   - API 키 자동 검증 및 경고 시스템
   - 필요한 디렉토리 자동 생성

## 성능 비교

- **기존 시스템**: 직접 구현으로 더 빠른 성능
- **Langchain 버전**: 약간의 오버헤드 있지만 유지보수성과 확장성, 안정성 대폭 향상

## 안정성 개선사항

1. **다중 fallback 시스템**: 주요 기능 실패 시 대체 방법 자동 실행
2. **자동 복구**: 일시적 오류 시 자동으로 재시도 및 복구
3. **상세한 로깅**: 문제 발생 시 정확한 원인 파악 가능
4. **환경 검증**: 실행 전 필요한 설정들 자동 검증
