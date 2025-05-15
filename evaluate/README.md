# RAG 시스템 성능 평가 모듈

이 폴더는 한국외국어대학교 컴퓨터공학과 RAG 챗봇 시스템의 성능을 평가하는 모듈들을 포함하고 있습니다.

## 개요

RAG(Retrieval-Augmented Generation) 시스템의 성능을 다음과 같은 지표로 평가합니다:

1. **Top-k 문서 정확도**: 시스템이 검색한 상위 k개 문서 중 정답 문서가 포함되었는지 평가
2. **응답 품질**: 생성된 응답의 품질을 ROUGE, BLEU 등의 메트릭으로 평가
3. **Reranker 성능**: 재정렬기(Reranker) 도입으로 인한 성능 향상을 평가
4. **시스템 비교**: 기존 RAG와 개선된 RAG의 응답을 비교

## 설치

필요한 패키지를 설치합니다:

```bash
pip install rouge-score nltk transformers torch
```

## 사용 방법

### 1. 테스트 데이터셋 생성

먼저 평가에 사용할 테스트 데이터셋을 생성합니다:

```bash
python -m evaluate.test_dataset
```

이 스크립트는 기본 테스트 데이터를 생성하며, 실제 평가를 위해서는 생성된 데이터셋을 수정하여 실제 문서 ID와 정답 응답을 매핑해야 합니다.

### 2. 전체 평가 실행

모든 평가 항목을 한번에 실행합니다:

```bash
python -m evaluate.evaluate
```

### 3. 개별 평가 실행

특정 평가만 선택적으로 실행할 수 있습니다:

```bash
# Top-k 정확도만 평가
python -m evaluate.evaluate --selective --top-k

# 응답 품질만 평가
python -m evaluate.evaluate --selective --quality

# Reranker 성능만 평가
python -m evaluate.evaluate --selective --reranker

# 시스템 비교만 실행 (특정 질의 사용)
python -m evaluate.evaluate --selective --comparison --query "컴퓨터공학과 졸업요건은 어떻게 되나요?"
```

### 4. 출력 경로 지정

평가 결과의 저장 위치를 지정할 수 있습니다:

```bash
python -m evaluate.evaluate --output-dir ./my_evaluation_results
```

## 모듈 설명

- `test_dataset.py`: 평가용 테스트 데이터셋 생성 및 관리
- `top_k_accuracy.py`: Top-k 문서 정확도 평가
- `response_quality.py`: GPT 응답 품질 평가 (ROUGE, BLEU 등)
- `reranker.py`: Reranker 구현 및 성능 평가
- `improved_rag.py`: Reranker를 적용한 개선된 RAG 시스템
- `evaluate.py`: 종합 평가 실행 모듈

## 결과 해석

평가 결과는 `evaluation_results` 디렉토리(또는 지정한 경로)에 JSON 파일로 저장됩니다:

- `top_k_accuracy.json`: Top-k 정확도 평가 결과
- `response_quality.json`: 응답 품질 평가 결과
- `reranker_improvement.json`: Reranker 성능 평가 결과
- `rag_comparison.json`: RAG 시스템 비교 결과
- `evaluation_summary.json`: 전체 평가 요약

## 추가 개선 방안

1. **휴먼 평가 추가**: 사람이 직접 응답 품질을 평가하는 모듈 추가
2. **평가 시각화**: 결과를 그래프로 시각화하는 기능 추가
3. **정답 문서 ID 자동 매핑**: 테스트 데이터셋의 정답 문서 ID를 자동으로 찾는 기능 구현
