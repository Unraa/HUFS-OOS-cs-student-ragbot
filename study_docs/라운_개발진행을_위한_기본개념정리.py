{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# 1. Baseline 코드 설명\n",
    "**목적**: OpenAI GPT-4o API를 활용하여 프롬프트 기반 응답 생성\n\n",
    "**구성 흐름:**\n",
    "- `.env` 파일에서 API 키 로드 (`dotenv`)\n",
    "- `prompts.yaml`에서 사용자 정의 프롬프트 불러오기\n",
    "- OpenAI 클라이언트로 GPT-4o에 프롬프트 전달 및 응답 생성\n",
    "- 예외 처리 및 결과 출력\n\n",
    "**의의**: 프롬프트-응답 기반 구조 이해에 적합한 실습 예제"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# 2. LLM(Large Language Model)이란?\n",
    "**정의**: 수십억 개의 파라미터로 구성된 대규모 언어 모델, 주로 Transformer 기반\n\n",
    "**작동 원리:**\n",
    "- **Pretraining**: 대규모 텍스트로 일반 언어 패턴 학습\n",
    "- **Fine-tuning** 또는 **Instruction tuning**으로 특정 작업 정밀화\n\n",
    "**주요 모델**: GPT, Claude, Gemini, LLaMA 등\n\n",
    "**장점**: 자연어 생성, 요약, 번역, 코드 작성 가능\n\n",
    "**단점**: 고비용, 편향, 최신 정보 부족, 제어 어려움"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# 3. LLM 기반 챗봇의 동작 과정\n",
    "1. **입력 수집**: 사용자로부터 자연어 문장 입력\n",
    "2. **전처리**: 입력을 토큰화하여 의미적 벡터로 변환\n",
    "3. **문맥 처리**: 대화 히스토리 포함하여 의미 이해\n",
    "4. **응답 생성**: 예측된 다음 토큰을 반복 생성하여 문장 형성\n",
    "5. **출력**: 사람이 이해할 수 있는 자연어로 응답 제공"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# 4. RAG(Retrieval-Augmented Generation) 아키텍처\n",
    "**정의**: LLM에 외부 지식 검색 기능을 결합한 하이브리드 아키텍처\n\n",
    "**동작 구조:**\n",
    "- 사용자 질문 → 임베딩 변환\n",
    "- 지식베이스에서 관련 문서 검색\n",
    "- 검색 결과 + 질문 → GPT에 입력 → 응답 생성\n\n",
    "**장점:**\n",
    "- 최신 정보 반영 가능\n",
    "- 기업 내부 문서와 결합 가능\n",
    "- 정확도 향상"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# 5. AWS를 활용한 프로젝트 배포\n",
    "**목표**: Gradio + RAG 챗봇을 Docker로 패키징 → AWS EC2에 배포\n\n",
    "**필수 준비:**\n",
    "- AWS 계정, EC2 인스턴스(Ubuntu), PEM 키, Docker 설치\n\n",
    "**기본 단계:**\n",
    "- 로컬에서 챗봇 서비스 개발 및 Docker 이미지 생성\n",
    "- EC2 인스턴스 설정 및 이미지 업로드\n",
    "- 포트 설정 및 실행 (`docker run -p 7860:7860 ...`)\n\n",
    "**결과**: 누구나 웹 브라우저에서 접속 가능한 챗봇 제공"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "name": "python",
   "version": "3.x"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}

