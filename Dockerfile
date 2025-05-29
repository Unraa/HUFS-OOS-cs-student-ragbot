FROM python:3.10-slim

WORKDIR /app

# requirements.txt 먼저 복사 → 캐시 유지
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 이후 전체 코드 복사
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
