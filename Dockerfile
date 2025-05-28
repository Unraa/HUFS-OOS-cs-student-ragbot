FROM python:3.10-slim

WORKDIR /app

# 환경 변수 설정
ARG OPENAI_API_KEY
ARG EMBEDDING_MODEL=text-embedding-3-small
ARG LLM_MODEL=gpt-4o
ARG CHROMA_DB_DIR=/app/data/chroma_db
ARG CHROMA_COLLECTION_NAME=hufs_cs_docs

ENV OPENAI_API_KEY=$OPENAI_API_KEY
ENV EMBEDDING_MODEL=$EMBEDDING_MODEL
ENV LLM_MODEL=$LLM_MODEL
ENV CHROMA_DB_DIR=$CHROMA_DB_DIR
ENV CHROMA_COLLECTION_NAME=$CHROMA_COLLECTION_NAME

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]