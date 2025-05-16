# 마크다운 기반 RAG 챗봇

이 프로젝트는 마크다운 문서를 ## 헤딩 기준으로 청킹하여 RAG(Retrieval-Augmented Generation) 챗봇을 구현합니다. 챗봇은 사용자 질문과 관련된 문서 조각(청크)을 검색하고, 이를 바탕으로 응답을 생성합니다.

## 주요 기능

- 주피터 노트북(.ipynb) 파일에서 마크다운 셀 추출 및 통합
- 마크다운 텍스트를 ## 헤딩 기준으로 청킹
- OpenAI API를 활용한 임베딩 생성
- 코사인 유사도 기반 유사 문서 검색
- 검색된 청크를 기반으로 LLM을 활용한 응답 생성

## 사용 방법

### 1. 환경 설정

```bash
# Conda 환경 설정 (선택사항)
conda create -n HUFS-OOS-cs-student-ragbot python=3.10
conda activate HUFS-OOS-cs-student-ragbot

# 필요한 패키지 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

루트 디렉토리에 `.env` 파일을 생성하고 OpenAI API 키를 설정합니다:

```
OPENAI_API_KEY=your_api_key_here
```

### 3. 실행 방법

#### 전체 파이프라인 실행 (처리 + 챗봇)

```bash
python code/run_pipeline.py
```

#### 옵션 사용

```bash
# 벡터 저장소 재구축
python code/run_pipeline.py --rebuild

# 특정 디렉토리의 문서 사용
python code/run_pipeline.py --docs_dir path/to/docs

# 벡터 저장소만 설정하고 챗봇 실행 안 함
python code/run_pipeline.py --setup_only
```

#### 챗봇만 실행

```bash
python code/rag_chatbot.py
```

## 파일 구조

- `markdown_processor.py` - 마크다운 문서 처리 및 청킹
- `embeddings_generator.py` - 임베딩 생성 및 벡터 저장소 관리
- `rag_chatbot.py` - RAG 기능 구현 및 챗봇 인터페이스
- `prompts.yaml` - 챗봇 프롬프트 설정
- `run_pipeline.py` - 전체 파이프라인 실행 스크립트

## 작동 원리

1. **문서 처리**: 주피터 노트북에서 마크다운 셀을 추출하여 하나의 문서로 통합
2. **청킹**: 통합된 문서를 ## 헤딩 기준으로 청크로 나눔
3. **임베딩 생성**: 각 청크에 대해 OpenAI API를 통해 임베딩 벡터 생성
4. **검색**: 사용자 질문에 대한 임베딩을 생성하고 코사인 유사도로 관련 청크 검색
5. **응답 생성**: 검색된 청크를 컨텍스트로 활용하여 LLM을 통해 응답 생성

## 주의사항

- OpenAI API 키가 필요합니다.
- 처리할 문서의 양이 많을 경우 API 비용이 발생할 수 있습니다.
- 초기 벡터 저장소 구축에는 시간이 소요될 수 있습니다.
