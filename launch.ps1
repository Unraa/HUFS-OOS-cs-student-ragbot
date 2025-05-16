# =====================================================================
# 실행 방법:
# 1. PowerShell에서: .\launch.ps1
# 2. 실행 정책 우회하여 실행: powershell -ExecutionPolicy Bypass -File launch.ps1
# 3. 관리자 권한으로 실행: 
#    powershell -ExecutionPolicy Bypass -Command "Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File launch.ps1' -Verb RunAs"
# =====================================================================

# 텍스트 색상 정의
$Green = [ConsoleColor]::Green
$Blue = [ConsoleColor]::Blue 
$Yellow = [ConsoleColor]::Yellow

# 헤더 출력
Write-Host "=========================================" -ForegroundColor $Blue
Write-Host "한국외국어대학교 컴퓨터공학과 RAG 챗봇 시작" -ForegroundColor $Green
Write-Host "=========================================" -ForegroundColor $Blue

# 현재 디렉토리를 PYTHONPATH에 추가
$env:PYTHONPATH = "$env:PYTHONPATH;$(Get-Location)"

# ChromaDB 디렉토리 확인
if (-not (Test-Path "data\chroma_db")) {
    Write-Host "ChromaDB 디렉토리가 없습니다. 자동으로 생성됩니다." -ForegroundColor $Yellow
    New-Item -Path "data\chroma_db" -ItemType Directory -Force | Out-Null
}

# FastAPI 서버 실행
Write-Host "FastAPI 서버 시작 중..." -ForegroundColor $Yellow
$process = Start-Process -FilePath "uvicorn" -ArgumentList "main:app --host 0.0.0.0 --port 8000 --reload" -PassThru -NoNewWindow

Write-Host "서비스가 시작되었습니다." -ForegroundColor $Green
Write-Host "FastAPI: http://localhost:8000" -ForegroundColor $Yellow
Write-Host "FastAPI 문서: http://localhost:8000/docs" -ForegroundColor $Yellow
Write-Host "챗봇 인터페이스: http://localhost:8000/chat" -ForegroundColor $Yellow
Write-Host "벡터 저장소 업데이트: http://localhost:8000/api/update-vector-store" -ForegroundColor $Yellow
Write-Host "----------------------------------------" -ForegroundColor $Blue
Write-Host "종료하려면 Ctrl+C를 누르세요." -ForegroundColor $Yellow

# 종료 이벤트 핸들러
try {
    # PowerShell에서 Ctrl+C 입력을 대기
    Wait-Process -Id $process.Id
}
finally {
    # 서버 프로세스 종료
    if (-not $process.HasExited) {
        Stop-Process -Id $process.Id -Force
    }
    Write-Host "서버가 종료되었습니다." -ForegroundColor $Yellow
} 